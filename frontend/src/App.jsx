
import { useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");

  const uploadDocument = async () => {
    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);
      setError("");

      const response = await axios.post(
        `${API}/api/documents/upload`,
        formData
      );

      setDocumentId(response.data.document_id);
      setDocumentName(response.data.filename);
      setMessages([]);

    } catch (err) {
      setError(
        err.response?.data?.detail || "Document upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  const askQuestion = async (e) => {
    e.preventDefault();

    if (!question.trim() || !documentId) return;

    const currentQuestion = question.trim();

    setMessages((previous) => [
      ...previous,
      { role: "user", text: currentQuestion }
    ]);

    setQuestion("");
    setAsking(true);
    setError("");

    try {
      const response = await axios.post(
        `${API}/api/documents/${documentId}/ask`,
        { question: currentQuestion }
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: response.data.answer,
          pages: response.data.source_pages
        }
      ]);

    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to generate an answer."
      );
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">

      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">D</div>
          <span>DocuMind<span className="brand-ai"> AI</span></span>
        </div>

        <div className="header-label">
          Document Intelligence Assistant
        </div>
      </header>

      <main className="workspace">

        <section className="sidebar">
          <h3>Workspace</h3>

          <div className="upload-card">
            <div className="upload-icon">↑</div>

            <h3>Upload document</h3>

            <p>Choose a PDF to start asking questions.</p>

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => {
                setFile(e.target.files[0] || null);
                setError("");
              }}
            />

            <button
              className="primary-button upload-button"
              onClick={uploadDocument}
              disabled={uploading || !file}
            >
              {uploading ? "Processing..." : "Upload PDF"}
            </button>
          </div>

          {documentId && (
            <div className="document-card">
              <span className="pdf-icon">PDF</span>
              <div>
                <strong>{documentName}</strong>
                <p>Indexed successfully</p>
              </div>
            </div>
          )}

          <div className="sidebar-footer">
            Powered by RAG technology
          </div>
        </section>

        <section className="chat-section">

          <div className="chat-heading">
            <div>
              <h2>Document Assistant</h2>
              <p>Ask questions and discover information in your documents.</p>
            </div>

            <span className="status">
              ● AI Assistant
            </span>
          </div>

          <div className="chat-body">

            {messages.length === 0 && (
              <div className="welcome">
                <div className="welcome-icon">✦</div>
                <h1>Your documents, understood.</h1>
                <p>
                  Upload a PDF and ask questions.
                  DocuMind AI will find relevant information for you.
                </p>

                {!documentId && (
                  <div className="empty-hint">
                    Upload a PDF from the left panel to begin.
                  </div>
                )}
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role}`}
              >
                <div className="message-label">
                  {message.role === "user" ? "You" : "DocuMind AI"}
                </div>

                <div className="message-text">
                  {message.text}
                </div>

                {message.pages?.length > 0 && (
                  <div className="source">
                    Sources: Page {message.pages.join(", ")}
                  </div>
                )}
              </div>
            ))}

            {asking && (
              <div className="loading-message">
                DocuMind AI is processing your question...
              </div>
            )}

          </div>

          {error && (
            <div className="error-message">{error}</div>
          )}

          <form className="chat-input" onSubmit={askQuestion}>
            <input
              type="text"
              placeholder={
                documentId
                  ? "Ask anything about your document..."
                  : "Upload a document to start..."
              }
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!documentId || asking}
            />

            <button
              type="submit"
              className="primary-button"
              disabled={!documentId || asking || !question.trim()}
            >
              {asking ? "..." : "Ask"}
            </button>
          </form>

          <p className="disclaimer">
            AI-generated answers should be verified against the original document.
          </p>

        </section>

      </main>
    </div>
  );
}

export default App;
