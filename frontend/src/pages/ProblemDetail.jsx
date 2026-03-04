import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import Editor from "@monaco-editor/react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import { useTheme } from "../context/ThemeContext";
import "./ProblemDetail.css";

const defaultCode = `def solve():
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        return
    # TODO: implement solution
    print("")

if __name__ == "__main__":
    solve()
`;

const ProblemDetail = () => {
  const { problemId } = useParams();
  const { theme } = useTheme();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState(defaultCode);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProblem = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await api.get(`/problem/${problemId}`);
        setProblem(response.data?.data || null);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load problem.");
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [problemId]);

  const editorTheme = useMemo(() => {
    if (theme === "dark" || theme === "neon") {
      return "vs-dark";
    }
    return "vs";
  }, [theme]);

  const handleRun = async () => {
    if (!problem) {
      return;
    }

    try {
      setRunning(true);
      setError("");
      const response = await api.post("/run", {
        problem_id: problem.id,
        code,
      });
      const data = response.data?.data;
      setResults(data?.results || []);
      setSummary({
        passed_count: data?.passed_count || 0,
        total_count: data?.total_count || 0,
        runtime_ms: data?.runtime_ms || 0,
        status: "Run Complete",
      });
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to run code.");
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!problem) {
      return;
    }

    try {
      setRunning(true);
      setError("");
      const response = await api.post("/submit", {
        problem_id: problem.id,
        code,
        language: "python",
      });
      const data = response.data?.data;
      setSummary({
        passed_count: data?.passed_count || 0,
        total_count: data?.total_count || 0,
        runtime_ms: data?.runtime_ms || 0,
        status: data?.status || "Submitted",
      });
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to submit code.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <PageTransition>
      <div className="problem-detail-page">
        <div className="container-fluid py-4">
          {loading ? (
            <div className="problem-empty">Loading problem...</div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : problem ? (
            <>
              <div className="problem-detail-header">
                <div>
                  <span className={`pill pill--${problem.difficulty.toLowerCase()}`}>
                    {problem.difficulty}
                  </span>
                  <h1>{problem.title}</h1>
                </div>
                <div className="problem-actions">
                  <button
                    type="button"
                    className="btn btn-outline-primary"
                    onClick={handleRun}
                    disabled={running}
                  >
                    {running ? "Running..." : "Run Code"}
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={running}
                  >
                    {running ? "Submitting..." : "Submit Solution"}
                  </button>
                </div>
              </div>

              <div className="problem-detail-grid">
                <section className="problem-description">
                  <div className="problem-section">
                    <h5>Description</h5>
                    <p>{problem.description}</p>
                  </div>
                  <div className="problem-section">
                    <h6>Example</h6>
                    <div className="problem-example">
                      <div>
                        <strong>Input</strong>
                        <pre>{problem.example_input || "-"}</pre>
                      </div>
                      <div>
                        <strong>Output</strong>
                        <pre>{problem.example_output || "-"}</pre>
                      </div>
                    </div>
                  </div>
                  {problem.constraints ? (
                    <div className="problem-section">
                      <h6>Constraints</h6>
                      <p>{problem.constraints}</p>
                    </div>
                  ) : null}
                  <div className="problem-section">
                    <h6>Tags</h6>
                    <div className="problem-tags">
                      {problem.tags?.length
                        ? problem.tags.map((tag) => <span key={tag}>{tag}</span>)
                        : "No tags"}
                    </div>
                  </div>
                </section>

                <section className="problem-editor">
                  <Editor
                    height="100%"
                    language="python"
                    theme={editorTheme}
                    value={code}
                    onChange={(value) => setCode(value || "")}
                    options={{
                      fontSize: 14,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                    }}
                  />
                </section>
              </div>

              <section className="problem-results">
                <div className="problem-results__header">
                  <h5 className="mb-0">Test Results</h5>
                  {summary ? (
                    <span className="problem-results__summary">
                      {summary.status} · {summary.passed_count}/{summary.total_count} · {summary.runtime_ms}ms
                    </span>
                  ) : (
                    <span className="problem-results__summary">Run or submit to see results.</span>
                  )}
                </div>
                <div className="problem-results__body">
                  {results.length ? (
                    results.map((result, index) => (
                      <div
                        key={`result-${index}`}
                        className={`result-card ${result.passed ? "pass" : "fail"}`}
                      >
                        <div>
                          <strong>Case {index + 1}</strong>
                          <span>{result.passed ? "Passed" : "Failed"}</span>
                        </div>
                        {result.error ? (
                          <div className="result-error">{result.error}</div>
                        ) : (
                          <div className="result-output">
                            <div>
                              <small>Expected</small>
                              <pre>{result.expected_output}</pre>
                            </div>
                            <div>
                              <small>Your Output</small>
                              <pre>{result.actual_output}</pre>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="problem-empty">No results yet.</div>
                  )}
                </div>
              </section>
            </>
          ) : (
            <div className="problem-empty">Problem not found.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default ProblemDetail;
