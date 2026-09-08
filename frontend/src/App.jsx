import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const suggestions = [
  {
    icon: "⌕",
    title: "Find authentication",
    text: "Where is authentication implemented?",
  },
  {
    icon: "</>",
    title: "Explain an API",
    text: "Explain how the main API works.",
  },
  {
    icon: "◎",
    title: "Trace a function",
    text: "Where is JWT validation implemented?",
  },
  {
    icon: "⌘",
    title: "Understand architecture",
    text: "How do the main files work together?",
  },
];

function App() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const [projectLoaded, setProjectLoaded] = useState(false);
  const [projectInfo, setProjectInfo] = useState(null);

  const uploadProject = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError("Please upload a ZIP file.");
      return;
    }

    setUploading(true);
    setError("");
    setAnswer("");
    setSources([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Upload failed.");
      }

      setProjectLoaded(true);

      setProjectInfo({
        filename: data.filename,
        files: data.files,
        chunks: data.chunks,
      });
    } catch (err) {
      setProjectLoaded(false);
      setProjectInfo(null);
      setError(err.message || "Could not upload project.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const askDevPilot = async (question = message) => {
    const text = question.trim();

    if (!text || loading) return;

    if (!projectLoaded) {
      setError("Upload a project ZIP before asking questions.");
      return;
    }

    setMessage(text);
    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "DevPilot could not process the request.",
        );
      }

      setAnswer(
        data.answer ||
          "DevPilot could not generate an answer from the available code.",
      );

      setSources(data.sources || []);
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong while communicating with DevPilot.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askDevPilot();
    }
  };

  const startNewChat = () => {
    setMessage("");
    setAnswer("");
    setSources([]);
    setError("");
  };

  const useSuggestion = (text) => {
    setMessage(text);
    askDevPilot(text);
  };

  return (
    <div className="app-shell">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">D</div>

          <div>
            <div className="brand-name">DevPilot</div>
            <div className="brand-subtitle">Developer Intelligence</div>
          </div>
        </div>

        <button className="new-chat-button" onClick={startNewChat}>
          <span>＋</span>
          <span>New conversation</span>
        </button>

        <div className="sidebar-section">
          <div className="section-label">CODEBASE</div>

          <label className="upload-button">
            <span className="upload-icon">↥</span>
            <span>{uploading ? "Indexing..." : "Upload ZIP"}</span>

            <input
              type="file"
              accept=".zip"
              onChange={uploadProject}
              disabled={uploading}
            />
          </label>
        </div>

        {projectInfo && (
          <div className="project-card">
            <div className="project-card-header">
              <div className="project-file-icon">ZIP</div>

              <div className="project-details">
                <div className="project-name" title={projectInfo.filename}>
                  {projectInfo.filename}
                </div>

                <div className="project-status">
                  <span className="status-dot" />
                  Ready
                </div>
              </div>
            </div>

            <div className="project-stats">
              <div>
                <strong>{projectInfo.files}</strong>
                <span>Files</span>
              </div>

              <div>
                <strong>{projectInfo.chunks}</strong>
                <span>Chunks</span>
              </div>
            </div>
          </div>
        )}

        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <div className="note-icon">✦</div>

            <div>
              <strong>Codebase aware</strong>
              <span>
                Ask questions about the uploaded project's implementation.
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-panel">
        {/* HEADER */}
        <header className="topbar">
          <div>
            <div className="page-title">Codebase Explorer</div>
            <div className="page-subtitle">
              Ask questions. Understand your code.
            </div>
          </div>

          <div
            className={`connection-status ${
              projectLoaded ? "ready" : "waiting"
            }`}
          >
            <span className="connection-dot" />

            {projectLoaded ? "Codebase Ready" : "Upload a codebase"}
          </div>
        </header>

        {/* CONTENT */}
        <section className="content-area">
          {!answer && !loading && !error ? (
            <div className="welcome-container">
              <div className="hero-icon">
                <div className="hero-icon-inner">D</div>
              </div>

              <div className="eyebrow">AI DEVELOPER AGENT</div>

              <h1>
                Understand your
                <br />
                <span>codebase faster.</span>
              </h1>

              <p className="hero-description">
                Upload a project and ask DevPilot where things are, how they
                work, and how different parts of your code connect.
              </p>

              {!projectLoaded ? (
                <div className="upload-prompt">
                  <div className="upload-prompt-icon">↑</div>

                  <div>
                    <strong>Upload your codebase</strong>

                    <span>
                      ZIP files only · Your files stay within this session
                    </span>
                  </div>

                  <label className="small-upload">
                    {uploading ? "Processing..." : "Choose ZIP"}

                    <input
                      type="file"
                      accept=".zip"
                      onChange={uploadProject}
                      disabled={uploading}
                    />
                  </label>
                </div>
              ) : (
                <div className="ready-banner">
                  <span className="ready-check">✓</span>

                  <div>
                    <strong>{projectInfo?.filename}</strong>
                    <span>
                      {projectInfo?.files} files indexed and ready to explore
                    </span>
                  </div>
                </div>
              )}

              <div className="suggestions-heading">
                <span>Try asking</span>
              </div>

              <div className="suggestions-grid">
                {suggestions.map((item) => (
                  <button
                    className="suggestion-card"
                    key={item.title}
                    onClick={() => useSuggestion(item.text)}
                    disabled={!projectLoaded || loading}
                  >
                    <div className="suggestion-icon">{item.icon}</div>

                    <div className="suggestion-content">
                      <strong>{item.title}</strong>
                      <span>{item.text}</span>
                    </div>

                    <span className="suggestion-arrow">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="conversation">
              {message && (
                <div className="user-message">
                  <div className="message-avatar user-avatar">You</div>

                  <div className="user-message-content">
                    <div className="message-label">You</div>
                    <div className="user-question">{message}</div>
                  </div>
                </div>
              )}

              {loading && (
                <div className="assistant-message">
                  <div className="message-avatar assistant-avatar">D</div>

                  <div className="assistant-content">
                    <div className="message-label">DevPilot</div>

                    <div className="thinking-card">
                      <div className="thinking-icon">✦</div>

                      <div>
                        <strong>Analyzing your codebase</strong>
                        <span>
                          Searching relevant files and understanding the
                          implementation...
                        </span>
                      </div>

                      <div className="thinking-dots">
                        <span />
                        <span />
                        <span />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {error && !loading && (
                <div className="error-card">
                  <div className="error-icon">!</div>

                  <div>
                    <strong>Something went wrong</strong>
                    <span>{error}</span>
                  </div>

                  <button
                    onClick={() => askDevPilot()}
                    disabled={!message || loading}
                  >
                    Retry
                  </button>
                </div>
              )}

              {answer && !loading && (
                <div className="assistant-message">
                  <div className="message-avatar assistant-avatar">D</div>

                  <div className="assistant-content">
                    <div className="message-label">DevPilot</div>

                    <div className="answer-card">
                      <div className="answer-text">
                        {answer.split("\n").map((line, index) => (
                          <p key={index}>{line || "\u00A0"}</p>
                        ))}
                      </div>
                    </div>

                    {sources.length > 0 && (
                      <div className="sources-section">
                        <div className="sources-header">
                          <span>Sources</span>
                          <span className="sources-count">
                            {sources.length} references
                          </span>
                        </div>

                        <div className="sources-list">
                          {sources.map((source, index) => (
                            <div
                              className="source-item"
                              key={`${source.path}-${source.start_line}-${index}`}
                            >
                              <div className="source-file-icon">
                                {source.language === "Python"
                                  ? "PY"
                                  : source.language === "JavaScript"
                                    ? "JS"
                                    : source.language === "React JSX"
                                      ? "JSX"
                                      : "CODE"}
                              </div>

                              <div className="source-main">
                                <div className="source-path">{source.path}</div>

                                <div className="source-meta">
                                  {source.language}
                                  <span>•</span>
                                  Lines {source.start_line}–{source.end_line}
                                </div>
                              </div>

                              <div className="source-arrow">↗</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* INPUT */}
        <div className="composer-wrapper">
          <div className="composer">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                projectLoaded
                  ? "Ask anything about your codebase..."
                  : "Upload a ZIP to start exploring your codebase..."
              }
              disabled={!projectLoaded || loading}
              rows={1}
            />

            <button
              className="send-button"
              onClick={() => askDevPilot()}
              disabled={!projectLoaded || !message.trim() || loading}
              aria-label="Send message"
            >
              ↑
            </button>
          </div>

          <div className="composer-footer">
            <span>
              DevPilot can make mistakes. Verify important implementation
              details in your source code.
            </span>

            <span>Enter to send · Shift + Enter for new line</span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
