import json
import os
import re
import uuid
from typing import Any, Dict, List

from dotenv import load_dotenv
from git import Repo
from langchain_openai import ChatOpenAI

from backend.src.agent.prompts import (
    _get_file_selection_prompt,
    _get_summarization_prompt,
)

from .state import AgentState

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
# Defaulting to 4o if Nano isn't set
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o")
model = ChatOpenAI(
    api_key=API_KEY,
    model=MODEL_NAME,
    temperature=0,
    max_retries=2,
)


def _generate_readme_file(content: str, target_dir: str) -> str:
    """Helper function to write README.md to the target directory."""
    readme_path = os.path.join(target_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    return readme_path


def extract_json_list(text: str) -> List[str]:
    """
    Robustly extracts a JSON list from a string that might contain
    markdown code blocks or conversational filler.
    """
    # 1. Try to find content inside ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    # 2. If no backticks, try to find the first '[' and last ']'
    else:
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        if match:
            text = match.group(1)

    # 3. Final cleanup and load
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # Fallback: simple split if the LLM fails completely (or return empty)
        return []


def cloner_node(state: AgentState) -> Dict[str, Any]:
    repo_url = state.get("repo_url")
    logs = state.get("logs", [])

    # Create a unique folder name
    # We combine a "repo-slug" with a UUID for uniqueness
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    unique_id = uuid.uuid4().hex[:8]
    folder_name = f"{repo_name}_{unique_id}"

    # Define the target path
    base_dir = os.path.join("data")
    target_path = os.path.abspath(os.path.join(base_dir, unique_id, folder_name))

    # Ensure the base directory exists
    os.makedirs(os.path.join(base_dir, unique_id), exist_ok=True)

    try:
        # Perform the shallow clone
        logs.append(f"Starting shallow clone of {repo_url} into {target_path}")
        Repo.clone_from(repo_url, target_path, depth=1)

        logs.append("Clone successful.")

        # Update and return the state
        return {"local_path": target_path, "logs": logs, "unique_id": unique_id}

    except Exception as e:
        error_msg = f"Failed to clone repository: {str(e)}"
        logs.append(error_msg)
        return {"logs": logs, "local_path": "ERROR"}


def generate_tree(root_dir: str) -> str:
    """Generates a text-based tree, excluding common noise."""
    tree = []
    # Ignore patterns to save tokens and avoid LLM confusion
    exclude_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".env",
        "dist",
        "build",
    }

    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        level = root.replace(root_dir, "").count(os.sep)
        indent = " " * 4 * level
        folder_name = os.path.basename(root) or root_dir
        tree.append(f"{indent}{folder_name}/")

        sub_indent = " " * 4 * (level + 1)
        for f in files:
            # Basic non-text file extension filter
            if not f.endswith((".png", ".jpg", ".jpeg", ".gif", ".pyc", ".exe")):
                tree.append(f"{sub_indent}{f}")

    return "\n".join(tree)


def manager_node(state: AgentState) -> Dict[str, Any]:
    local_path = state["local_path"]
    logs = state.get("logs", [])

    logs.append("Generating file tree for analysis...")
    file_tree_str = generate_tree(local_path)
    prompt = _get_file_selection_prompt(file_tree_str)

    try:
        # LLM call
        logs.append(f"Step: Consulting {MODEL_NAME} for file selection...")
        messages = [
            (
                "system",
                "You are a helpful assistant that outputs only " "raw JSON lists.",
            ),
            ("human", prompt),
        ]
        selected_files = []
        try:
            response = model.invoke(messages)
            selected_files = extract_json_list(response.content)
        except Exception as e:
            logs.append(f"LLM call failed: {str(e)}")
            return {"logs": logs, "selected_files": []}

        # Ensure paths are absolute for the next nodes to use easily
        full_paths = [os.path.join(local_path, f.lstrip("/")) for f in selected_files]

        logs.append(f"LLM selected {len(full_paths)} files for analysis.")

        return {"selected_files": full_paths, "logs": logs}

    except Exception as e:
        logs.append(f"Error in Manager Node: {str(e)}")
        return {"logs": logs, "selected_files": []}


def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarizes all files listed in state["selected_files"] and returns
    a list of summary objects.
    """
    selected_files = state.get("selected_files", [])
    all_summaries: List[Dict[str, Any]] = []

    for file_path in selected_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()

            base_file_path = os.path.basename(file_path)
            prompt = _get_summarization_prompt(code_content, base_file_path)

            messages = [("human", prompt)]
            response = model.invoke(messages)
            summary_data = json.loads(response.content)
            all_summaries.append(summary_data)

        except Exception as e:
            all_summaries.append({"file": file_path, "error": str(e)})

    return {"summaries": all_summaries}


def writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    summaries = state.get("summaries", [])
    repo_url = state.get("repo_url", "the repository")
    logs = state.get("logs", [])

    if not summaries:
        logs.append("Writer Node: No summaries found to synthesize.")
        return {
            "final_report": "Error: No analysis data available.",
            "logs": logs,
        }

    logs.append(
        f"Writer Node: Synthesizing {len(summaries)} file analyses " f"into a README..."
    )

    # 1. Prepare the aggregated context
    # We join all analyst findings into one big block for the
    # "Conductor" to read
    combined_summaries = "\n\n".join(
        [
            f"--- File: {(
                s.get('file') or s.get('file_path') or 'unknown'
            )} ---\n{(s.get('summary') or '')}"
            for s in summaries
            if isinstance(s, dict)
        ]
    )

    # 2. The Synthesizer Prompt
    prompt = f"""
    You are a Senior Technical Writer. Using the following
    file-level analyses from {repo_url}, create a professional,
    comprehensive README.md file.

    ### Data Source (File Summaries):
    {combined_summaries}

    ### README Requirements:
    - **Title**: A clear name for the project.
    - **Overview**: A high-level explanation of what this tool does.
    - **Architecture**: Explain how the analyzed files (entry points
      and core logic) work together.
    - **Key Features**: List the main functionalities discovered.
    - **Usage/Setup**: Based on the configuration and logic files,
      infer how to run this.

    Use clean Markdown formatting with H1, H2, and code blocks.
    """

    try:
        # 3. Call the LLM to generate the narrative
        messages = [
            (
                "system",
                "You are an expert technical documentarian.",
            ),
            ("human", prompt),
        ]
        response = model.invoke(messages)

        final_readme = response.content
        unique_id = state.get("unique_id", "default_id")
        base_dir = os.path.join("data")
        target_path = os.path.abspath(os.path.join(base_dir, unique_id))
        _generate_readme_file(final_readme, target_path)
        logs.append("Writer Node: Successfully generated README.md.")
        return {"final_report": final_readme, "logs": logs}

    except Exception as e:
        error_msg = f"Error in Writer Node: {str(e)}"
        logs.append(error_msg)
        return {
            "final_report": "Failed to generate documentation.",
            "logs": logs,
        }
