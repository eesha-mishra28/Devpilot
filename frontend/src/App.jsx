import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">D</div>
          <span>DevPilot</span>
        </div>

        <button className="new-chat">+ New Chat</button>

        <div className="recent">
          <p className="section-title">RECENT CHATS</p>

          <div className="chat-item">Authentication flow</div>

          <div className="chat-item">Task creation API</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main">
        {/* Header */}
        <header className="header">
          <div>
            <h1>DevPilot</h1>
            <p>AI Code Assistant</p>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            Ready
          </div>
        </header>

        {/* Chat Area */}
        <section className="chat-area">
          <div className="welcome">
            <div className="welcome-icon">D</div>

            <h2>Welcome to DevPilot</h2>

            <p>
              Ask questions about your codebase and understand how your
              application works.
            </p>

            <div className="suggestions">
              <button
                onClick={() =>
                  setMessage("Where is authentication implemented?")
                }
              >
                Where is authentication implemented?
              </button>

              <button onClick={() => setMessage("Explain how this API works.")}>
                Explain how this API works.
              </button>

              <button
                onClick={() => setMessage("Which files handle JWT validation?")}
              >
                Which files handle JWT validation?
              </button>
            </div>
          </div>
        </section>

        {/* Input */}
        <div className="input-container">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask DevPilot about your codebase..."
            rows="1"
          />

          <button className="send-button">Send</button>
        </div>

        <p className="footer-text">
          DevPilot can make mistakes. Verify important information.
        </p>
      </main>
    </div>
  );
}

export default App;
