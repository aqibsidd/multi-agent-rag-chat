import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = "";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [sessionId, setSessionId] = useState(() => {
    let id = localStorage.getItem("rag_session_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("rag_session_id", id);
    }
    return id;
  });
  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Restore conversation log for this session (SQLite checkpointer server-side).
    fetch(`${API_BASE}/chat/history/${sessionId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.messages)) {
          setMessages(data.messages.map((m) => ({ ...m, sources: [], trace: [] })));
        }
      })
      .catch(() => {});
  }, [sessionId]);

  function newChat() {
    const id = crypto.randomUUID();
    localStorage.setItem("rag_session_id", id);
    setSessionId(id);
    setMessages([]);
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploadStatus(`Ingesting ${file.name}...`);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/ingest/file`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setUploadStatus(`Added "${file.name}" (${data.chunks_added} chunks) to knowledge base.`);
    } catch (err) {
      setUploadStatus(`Failed to ingest file: ${err.message}`);
    } finally {
      fileInputRef.current.value = "";
    }
  }

  async function sendMessage() {
    const text = input.trim();
    if (!text || isStreaming) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setIsStreaming(true);

    // placeholder assistant message we will stream tokens into
    setMessages((prev) => [...prev, { role: "assistant", content: "", sources: [], trace: [] }]);

    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop(); // keep incomplete block for next read

        for (const block of blocks) {
          const eventLine = block.split("\n").find((l) => l.startsWith("event: "));
          const dataLine = block.split("\n").find((l) => l.startsWith("data: "));
          if (!eventLine || !dataLine) continue;

          const event = eventLine.slice("event: ".length);
          const payload = JSON.parse(dataLine.slice("data: ".length));

          if (event === "agent") {
            setMessages((prev) => {
              const copy = [...prev];
              copy[copy.length - 1] = {
                ...copy[copy.length - 1],
                trace: [...copy[copy.length - 1].trace, { node: payload.node, route: payload.route }],
              };
              return copy;
            });
          } else if (event === "token") {
            setMessages((prev) => {
              const copy = [...prev];
              copy[copy.length - 1] = {
                ...copy[copy.length - 1],
                content: copy[copy.length - 1].content + payload.text,
              };
              return copy;
            });
          } else if (event === "done") {
            setMessages((prev) => {
              const copy = [...prev];
              copy[copy.length - 1] = {
                ...copy[copy.length - 1],
                sources: payload.sources,
              };
              return copy;
            });
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: `Error: ${err.message}` };
        return copy;
      });
    } finally {
      setIsStreaming(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Multi-Agent RAG Chat</h1>
        <p className="subtitle">Ollama + LangGraph + Qdrant — fully local</p>
      </header>

      <div className="upload-bar">
        <input
          type="file"
          accept=".txt,.md,.pdf,.png,.jpg,.jpeg"
          ref={fileInputRef}
          onChange={handleFileUpload}
        />
        <button onClick={newChat} disabled={isStreaming} title="Start a fresh session">
          New chat
        </button>
        {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
      </div>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state">
            Upload a document, then ask a question about it below.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="bubble">
              {m.trace && m.trace.length > 0 && (
                <div className="trace">
                  {m.trace.map((t, j) => (
                    <span key={j} className={`trace-badge trace-${t.node}`}>
                      {t.node}
                      {t.route ? `: ${t.route}` : ""}
                    </span>
                  ))}
                </div>
              )}
              <div className="content">
                {m.content ? (
                  m.role === "assistant" ? (
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  ) : (
                    m.content
                  )
                ) : isStreaming && i === messages.length - 1 ? (
                  "…"
                ) : (
                  ""
                )}
              </div>
              {m.sources && m.sources.length > 0 && (
                <details className="sources">
                  <summary>{m.sources.length} source chunk(s)</summary>
                  {m.sources.map((s, j) => (
                    <div key={j} className="source-item">
                      <strong>{s.source}</strong>: {s.preview}...
                    </div>
                  ))}
                </details>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about your documents..."
          rows={2}
        />
        <button onClick={sendMessage} disabled={isStreaming || !input.trim()}>
          {isStreaming ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
