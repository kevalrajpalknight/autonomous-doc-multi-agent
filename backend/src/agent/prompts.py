def _get_file_selection_prompt(file_tree_str) -> str:
    return f"""
    You are a Technical Lead. Below is the file structure of a
    software repository.
    
    ### File Tree:
    {file_tree_str}
    
    ### Task:
    Identify the core logic files, entry points, and configuration
    files required to understand how this project works.
    
    ### Constraints:
    - Return ONLY a raw JSON list of relative file paths.
    - Exclude images, lockfiles (package-lock.json, poetry.lock),
      and documentation like README unless it's critical.
    - No conversational filler.
    
    Example Output: ["src/main.py", "config/settings.yaml",
    "api/routes.py"]"""


def _get_summarization_prompt(code_content, base_file_path) -> str:
    return f"""You are an expert software engineer tasked with summarizing code changes in a repository. Your goal is to create a concise and informative summary of the changes made, focusing on the key modifications, additions, and deletions.
            Analyze this source code file: {base_file_path}
            
            ### Code:
            {code_content}
            
            ### Task:
            Provide a concise summary:
            1. Purpose of the file.
            2. Key functions/classes defined.
            3. Major dependencies.
            
            Return the result as a JSON object:
            {{ "file": "filename", "summary": "...",
               "exports": [...], "deps": [...] }}"""
