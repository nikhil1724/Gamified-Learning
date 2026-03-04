import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import PageTransition from "../components/PageTransition";
import "./ProblemsList.css";

const ProblemsList = () => {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState("all");

  useEffect(() => {
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

    fetchProblems();
  }, []);

  const filteredProblems = useMemo(() => {
    return problems.filter((problem) => {
      const matchesSearch = problem.title
        .toLowerCase()
        .includes(search.trim().toLowerCase());
      const matchesDifficulty =
        difficulty === "all" || problem.difficulty === difficulty;
      return matchesSearch && matchesDifficulty;
    });
  }, [problems, search, difficulty]);

  return (
    <PageTransition>
      <div className="problems-page">
        <div className="container py-5">
          <div className="problems-hero">
            <div>
              <span className="problem-badge">Coding Arena</span>
              <h1>Practice Problems</h1>
              <p className="text-muted">
                Solve curated challenges and earn XP as you progress.
              </p>
            </div>
            <div className="problems-filters">
              <input
                className="form-control"
                placeholder="Search problems"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <select
                className="form-select"
                value={difficulty}
                onChange={(event) => setDifficulty(event.target.value)}
              >
                <option value="all">All difficulty</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>

          {error ? <div className="alert alert-danger">{error}</div> : null}

          <div className="problems-grid">
            {loading ? (
              <div className="problems-empty">Loading problems...</div>
            ) : filteredProblems.length ? (
              filteredProblems.map((problem) => (
                <Link
                  key={problem.id}
                  to={`/problems/${problem.id}`}
                  className="problem-card"
                >
                  <div className="problem-card__header">
                    <h5>{problem.title}</h5>
                    <span
                      className={`pill pill--${problem.difficulty.toLowerCase()}`}
                    >
                      {problem.difficulty}
                    </span>
                  </div>
                  <div className="problem-card__tags">
                    {problem.tags?.length
                      ? problem.tags.map((tag) => <span key={tag}>{tag}</span>)
                      : "No tags"}
                  </div>
                </Link>
              ))
            ) : (
              <div className="problems-empty">No problems match your filters.</div>
            )}
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default ProblemsList;
