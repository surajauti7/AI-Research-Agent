import { useState, useEffect } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";

function App() {
  const [question, setQuestion] = useState("");
  const [isListening, setIsListening] = useState(false);
const [speechSupported, setSpeechSupported] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const startVoiceSearch = () => {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    setSpeechSupported(false);
    setError("Voice search is not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();

  recognition.lang = "en-IN";
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    setIsListening(true);
    setError("");
  };

  recognition.onresult = (event) => {
    let transcript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }

    transcript = transcript.trim();

    if (transcript) {
      setQuestion(transcript);
    }
  };

  recognition.onerror = (event) => {
    setIsListening(false);

    if (event.error === "not-allowed") {
      setError("Microphone permission was denied. Please allow microphone access.");
    } else if (event.error === "no-speech") {
      setError("No speech detected. Please try speaking again.");
    } else {
      setError("Could not hear your voice. Please try again.");
    }
  };

  recognition.onend = () => {
    setIsListening(false);
  };

  recognition.start();
};

  const handleResearch = async () => {
    if (!question.trim()) {
      setError("Please enter a research question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("https://ai-research-agent-backend-2c6r.onrender.com/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to connect to the AI Research Agent. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleResearch();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">✦</span>
          <div>
            <h1>AI Research Agent</h1>
            <p>Search • Analyze • Summarize</p>
          </div>
        </div>
        <div className="status">
          <span className="status-dot"></span>
          AI Agent Online
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="badge">AI-POWERED RESEARCH</div>

          <h2>
            Research anything.
            <br />
            <span>Get intelligent answers.</span>
          </h2>

          <p className="hero-text">
            Ask a question and let the AI Research Agent search the web,
            analyze information, and generate a clear answer with sources.
          </p>

          <div className="search-box">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What would you like to research?"
              rows="3"
              disabled={loading}
            />

            <button
  type="button"
  onClick={startVoiceSearch}
  disabled={loading}
  className={`voice-button ${isListening ? "listening" : ""}`}
>
  {isListening ? "🎙️ Listening..." : "🎤 Voice Search"}
</button>

            <button
              onClick={handleResearch}
              disabled={loading}
              className="research-button"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Researching...
                </>
              ) : (
                <>
                  <span>✦</span>
                  Research
                </>
              )}
            </button>
          </div>

          <p className="hint">
            Press <strong>Enter</strong> to start research
          </p>

          {error && <div className="error">{error}</div>}
        </section>

        {loading && (
          <section className="loading-card">
            <div className="loading-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <h3>Researching your question...</h3>
            <p>
              Searching the web and preparing an AI-generated response.
            </p>
          </section>
        )}

        {result && !loading && (
          <section className="results">
            <div className="result-card">
              <div className="result-heading">
                <span className="result-icon">✓</span>
                <div>
                  <p className="result-label">YOUR QUESTION</p>
                  <h3>{result.question || question}</h3>
                </div>
              </div>

              <div className="answer">
  <div className="answer-header">
    <span className="answer-icon">✦</span>
    <p className="result-label">AI ANSWER</p>
  </div>

  <div className="answer-text">
    <ReactMarkdown
      components={{
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
          >
            {children}
          </a>
        ),
      }}
    >
      {result.answer || ""}
    </ReactMarkdown>
  </div>
              </div>

              {result.sources && result.sources.length > 0 && (
                <div className="sources">
                  <p className="result-label">SOURCES</p>

                  <div className="source-list">
                    {result.sources.map((source, index) => {
                      const url =
                        typeof source === "string"
                          ? source
                          : source.url || source.link;

                      return (
                        <a
                          key={index}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="source"
                        >
                          <span>{index + 1}</span>
                          <span className="source-url">
                            {url || JSON.stringify(source)}
                          </span>
                          <span>↗</span>
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      <footer>
        <p>AI Research Agent • Powered by Web Search + Gemini</p>
      </footer>
    </div>
  );
}

export default App;