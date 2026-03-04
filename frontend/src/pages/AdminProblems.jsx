import { useEffect, useMemo, useState } from "react";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./AdminProblems.css";

const emptyProblem = {
  title: "",
  difficulty: "Easy",
  tags: "",
  description: "",
  constraints: "",
  example_input: "",
  example_output: "",
};

const emptyTestCase = {
  input_data: "",
  expected_output: "",
  is_hidden: false,
};

const AdminProblems = () => {
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [problemForm, setProblemForm] = useState(emptyProblem);
  const [testCaseForm, setTestCaseForm] = useState(emptyTestCase);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [testCases, setTestCases] = useState([]);

  const fetchProblems = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await api.get("/problems");
      setProblems(response.data?.data || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load problems.");
    } finally {
      setLoading(false);
    }
  };

  const fetchProblemDetails = async (problemId) => {
    try {
      const response = await api.get(`/problem/${problemId}`);
      setTestCases(response.data?.data?.test_cases || []);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to load problem details.");
    }
  };

  useEffect(() => {
    fetchProblems();
  }, []);

  const difficultySummary = useMemo(() => {
    return problems.reduce(
      (acc, problem) => {
        acc[problem.difficulty] += 1;
        return acc;
      },
      { Easy: 0, Medium: 0, Hard: 0 }
    );
  }, [problems]);

  const handleProblemChange = (event) => {
    const { name, value } = event.target;
    setProblemForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleTestCaseChange = (event) => {
    const { name, value, type, checked } = event.target;
    setTestCaseForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleCreateProblem = async (event) => {
    event.preventDefault();
    setError("");

    try {
      setSaving(true);
      const payload = {
        ...problemForm,
        tags: problemForm.tags
          ? problemForm.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
          : [],
      };
      const response = await api.post("/admin/problems", payload);
      const createdId = response.data?.data?.id;
      setProblemForm(emptyProblem);
      await fetchProblems();
      if (createdId) {
        setSelectedProblem({ id: createdId, title: payload.title });
        await fetchProblemDetails(createdId);
      }
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to create problem.");
    } finally {
      setSaving(false);
    }
  };

  const handleSelectProblem = (problem) => {
    setSelectedProblem(problem);
    fetchProblemDetails(problem.id);
  };

  const handleAddTestCase = async (event) => {
    event.preventDefault();
    if (!selectedProblem) {
      setError("Select a problem before adding test cases.");
      return;
    }

    try {
      setSaving(true);
      await api.post(`/admin/problems/${selectedProblem.id}/test-cases`, testCaseForm);
      setTestCaseForm(emptyTestCase);
      fetchProblemDetails(selectedProblem.id);
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to add test case.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageTransition>
      <div className="admin-problems-page py-5">
        <div className="container">
          <div className="admin-problems-hero">
            <div>
              <span className="admin-badge">Admin Console</span>
              <h1 className="mb-2">Problem Manager</h1>
              <p className="text-muted mb-0">
                Create coding challenges and manage test cases.
              </p>
            </div>
            <div className="admin-problems-summary">
              <div>
                <span>Easy</span>
                <strong>{difficultySummary.Easy}</strong>
              </div>
              <div>
                <span>Medium</span>
                <strong>{difficultySummary.Medium}</strong>
              </div>
              <div>
                <span>Hard</span>
                <strong>{difficultySummary.Hard}</strong>
              </div>
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="admin-problems-grid">
            <section className="admin-panel">
              <div className="admin-panel__header">
                <h5 className="mb-0">All Problems</h5>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-primary"
                  onClick={fetchProblems}
                  disabled={loading}
                >
                  {loading ? "Refreshing..." : "Refresh"}
                </button>
              </div>
              <div className="admin-problem-list">
                {loading ? (
                  <div className="admin-empty">Loading problems...</div>
                ) : problems.length ? (
                  problems.map((problem) => (
                    <button
                      key={problem.id}
                      type="button"
                      className={`admin-problem-item ${
                        selectedProblem?.id === problem.id ? "is-active" : ""
                      }`}
                      onClick={() => handleSelectProblem(problem)}
                    >
                      <div>
                        <h6>{problem.title}</h6>
                        <span className={`pill pill--${problem.difficulty.toLowerCase()}`}>
                          {problem.difficulty}
                        </span>
                      </div>
                      <small className="text-muted">
                        {problem.tags?.length ? problem.tags.join(", ") : "No tags"}
                      </small>
                    </button>
                  ))
                ) : (
                  <div className="admin-empty">No problems yet.</div>
                )}
              </div>
            </section>

            <section className="admin-panel">
              <h5>Create Problem</h5>
              <form onSubmit={handleCreateProblem} className="admin-form">
                <input
                  className="form-control"
                  name="title"
                  placeholder="Problem title"
                  value={problemForm.title}
                  onChange={handleProblemChange}
                  required
                />
                <select
                  className="form-select"
                  name="difficulty"
                  value={problemForm.difficulty}
                  onChange={handleProblemChange}
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
                <input
                  className="form-control"
                  name="tags"
                  placeholder="Tags (comma separated)"
                  value={problemForm.tags}
                  onChange={handleProblemChange}
                />
                <textarea
                  className="form-control"
                  name="description"
                  placeholder="Problem description"
                  rows="5"
                  value={problemForm.description}
                  onChange={handleProblemChange}
                  required
                />
                <textarea
                  className="form-control"
                  name="constraints"
                  placeholder="Constraints"
                  rows="3"
                  value={problemForm.constraints}
                  onChange={handleProblemChange}
                />
                <textarea
                  className="form-control"
                  name="example_input"
                  placeholder="Example input"
                  rows="2"
                  value={problemForm.example_input}
                  onChange={handleProblemChange}
                />
                <textarea
                  className="form-control"
                  name="example_output"
                  placeholder="Example output"
                  rows="2"
                  value={problemForm.example_output}
                  onChange={handleProblemChange}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? "Saving..." : "Create Problem"}
                </button>
              </form>
            </section>

            <section className="admin-panel">
              <h5>Test Cases</h5>
              {selectedProblem ? (
                <>
                  <div className="admin-selected">
                    Selected: <strong>{selectedProblem.title}</strong>
                  </div>
                  <form onSubmit={handleAddTestCase} className="admin-form">
                    <textarea
                      className="form-control"
                      name="input_data"
                      placeholder="Input"
                      rows="3"
                      value={testCaseForm.input_data}
                      onChange={handleTestCaseChange}
                      required
                    />
                    <textarea
                      className="form-control"
                      name="expected_output"
                      placeholder="Expected output"
                      rows="2"
                      value={testCaseForm.expected_output}
                      onChange={handleTestCaseChange}
                      required
                    />
                    <label className="form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        name="is_hidden"
                        checked={testCaseForm.is_hidden}
                        onChange={handleTestCaseChange}
                      />
                      <span className="form-check-label">Hidden test case</span>
                    </label>
                    <button
                      type="submit"
                      className="btn btn-outline-primary"
                      disabled={saving}
                    >
                      {saving ? "Saving..." : "Add Test Case"}
                    </button>
                  </form>

                  <div className="admin-testcase-list">
                    <h6>Visible test cases</h6>
                    {testCases.length ? (
                      testCases.map((testCase) => (
                        <div key={testCase.id} className="admin-testcase">
                          <div>
                            <strong>Input</strong>
                            <pre>{testCase.input}</pre>
                          </div>
                          <div>
                            <strong>Expected Output</strong>
                            <pre>{testCase.expected_output}</pre>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="admin-empty">No public test cases yet.</div>
                    )}
                  </div>
                </>
              ) : (
                <div className="admin-empty">Select a problem to add test cases.</div>
              )}
            </section>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default AdminProblems;
