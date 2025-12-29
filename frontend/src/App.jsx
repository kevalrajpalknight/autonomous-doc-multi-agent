import { useCallback, useState } from "react";
import { InputSection } from "./components/InputSection";
import { MarkdownPreview } from "./components/MarkdownPreview";
import { Terminal } from "./components/Terminal";

function App() {
  const [logs, setLogs] = useState([]);
  const [markdown, setMarkdown] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);
  const [showMarkdown, setShowMarkdown] = useState(false);
  const [ws, setWs] = useState(null);

  const connectWebSocket = useCallback((repoUrl) => {
    const wsUrl = "ws://localhost:8000/ws/generate";
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log("WebSocket connected");
      websocket.send(JSON.stringify({ repo_url: repoUrl }));
      setIsLoading(true);
      setShowTerminal(true);
      setLogs([`Connecting to ${repoUrl}...`]);
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received:", data);

        if (data.status === "processing") {
          setLogs((prevLogs) => [
            ...prevLogs,
            data.log || data.node || "Processing...",
          ]);
        } else if (data.status === "completed") {
          if (data.markdown) {
            setMarkdown(data.markdown);
            setLogs((prevLogs) => [
              ...prevLogs,
              "✓ Documentation generated successfully!",
            ]);
            setTimeout(() => {
              setShowTerminal(false);
              setShowMarkdown(true);
            }, 1500);
          }
          setIsLoading(false);
        } else if (data.status === "error") {
          setLogs((prevLogs) => [...prevLogs, `✗ Error: ${data.message}`]);
          setIsLoading(false);
        }
      } catch (err) {
        console.error("Failed to parse message:", err);
        setLogs((prevLogs) => [...prevLogs, `Error: ${err.message}`]);
      }
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setLogs((prevLogs) => [
        ...prevLogs,
        "✗ Connection error. Make sure the backend is running on localhost:8000",
      ]);
      setIsLoading(false);
    };

    websocket.onclose = () => {
      console.log("WebSocket disconnected");
      setIsLoading(false);
    };

    setWs(websocket);
  }, []);

  const handleGenerate = useCallback(
    (url) => {
      setLogs([]);
      setMarkdown("");
      setShowTerminal(false);
      setShowMarkdown(false);
      connectWebSocket(url);
    },
    [connectWebSocket]
  );

  const handleCloseTerminal = () => {
    setShowTerminal(false);
    if (ws) {
      ws.close();
    }
  };

  const handleCloseMarkdown = () => {
    setShowMarkdown(false);
  };

  return (
    <div className="min-h-screen bg-black">
      {!showMarkdown && !showTerminal ? (
        <InputSection onGenerate={handleGenerate} isLoading={isLoading} />
      ) : null}

      <Terminal
        logs={logs}
        onClose={handleCloseTerminal}
        isVisible={showTerminal}
      />

      <MarkdownPreview
        markdown={markdown}
        onClose={handleCloseMarkdown}
        isVisible={showMarkdown}
      />
    </div>
  );
}

export default App;
