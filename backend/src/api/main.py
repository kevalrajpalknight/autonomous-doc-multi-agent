from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from starlette.websockets import WebSocketState

from ..agent.graph import app_graph

app = FastAPI(title="Autonomous Doc Agent API")


class RepoRequest(BaseModel):
    repo_url: str


@app.get("/")
def read_root():
    return {"status": "Agent API is running"}


@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receive the initial configuration from the frontend
        data = await websocket.receive_json()
        repo_url = data.get("repo_url")

        if not repo_url:
            await websocket.send_json({"error": "No repository URL provided."})
            return

        # Initialize the state
        initial_state = {
            "repo_url": repo_url,
            "logs": [f"Connection established. Target: {repo_url}"],
            "summaries": [],
            "selected_files": [],
        }

        # Stream the graph execution
        # We use 'astream' for async support within FastAPI
        async for event in app_graph.astream(
            initial_state, config={"configurable": {"thread_id": "1"}}
        ):
            # The event dictionary contains the output of the node that
            # just finished, e.g., {"cloner": {"logs": [...]}}
            for node_name, output in event.items():
                if "logs" in output:
                    # Send the latest log entries to the UI
                    new_logs = output["logs"]
                    # Usually, the state reducer appends logs,
                    # so we send the last one
                    latest_log = (
                        new_logs[-1] if new_logs else f"Node {node_name} completed."
                    )

                    await websocket.send_json(
                        {
                            "node": node_name,
                            "log": latest_log,
                            "status": "processing",
                        }
                    )
                # If the writer node is done, send the final result
                if node_name == "writer":
                    final_md = output.get("final_markdown") or output.get(
                        "final_report"
                    )
                    if final_md:
                        await websocket.send_json(
                            {"status": "completed", "markdown": final_md}
                        )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            if websocket.application_state == WebSocketState.CONNECTED:
                await websocket.send_json({"status": "error", "message": str(e)})
        except RuntimeError:
            pass
    finally:
        try:
            if websocket.application_state == WebSocketState.CONNECTED:
                await websocket.close()
        except RuntimeError:
            pass
