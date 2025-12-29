import operator
from typing import Annotated, Any, Dict, List

from typing_extensions import TypedDict


class AgentState(TypedDict):
    unique_id: str
    repo_url: str
    local_path: str
    file_tree: str
    selected_files: List[str]
    summaries: Annotated[List[Dict[str, Any]], operator.add]
    logs: Annotated[List[str], operator.add]
    final_markdown: str
