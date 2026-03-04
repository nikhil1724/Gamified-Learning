import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { publicApi } from "../services/api";
import PageTransition from "../components/PageTransition";
import "./SkillTree.css";

const SkillNode = ({ node, onSelect }) => {
  const isLocked = !node.unlocked;

  return (
    <li className={`skill-node ${isLocked ? "locked" : "unlocked"}`}>
      <div
        className={`card skill-card ${isLocked ? "text-muted" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => !isLocked && node.quiz_id && onSelect(node.quiz_id)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !isLocked && node.quiz_id) {
            onSelect(node.quiz_id);
          }
        }}
      >
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <h5 className="card-title mb-2">{node.skill_name}</h5>
            <span
              className={`badge ${
                node.unlocked ? "text-bg-success" : "text-bg-secondary"
              }`}
            >
              {node.unlocked ? "Unlocked" : "Locked"}
            </span>
          </div>
          <p className="card-text small">{node.description || ""}</p>
          {node.quiz_id ? (
            <span className="badge text-bg-primary">Start Quiz</span>
          ) : (
            <span className="badge text-bg-dark">No Quiz</span>
          )}
        </div>
      </div>
      {node.children && node.children.length > 0 ? (
        <ul>
          {node.children.map((child) => (
            <SkillNode key={child.id} node={child} onSelect={onSelect} />
          ))}
        </ul>
      ) : null}
    </li>
  );
};

const SkillTree = () => {
  const navigate = useNavigate();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        setLoading(true);
        const response = await publicApi.get("/skills");
        setSkills(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load skills.");
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  const handleSelectQuiz = (quizId) => {
    navigate(`/quiz?quizId=${quizId}`);
  };

  return (
    <PageTransition>
      <div className="container py-5">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2">
        <div>
          <h1 className="mb-2">Skill Tree</h1>
          <p className="text-muted mb-0">
            Unlock new skills as you complete quizzes.
          </p>
        </div>
      </div>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : null}

      {!loading && skills.length === 0 ? (
        <div className="alert alert-info">No skills available yet.</div>
      ) : null}

      {!loading && skills.length > 0 ? (
        <div className="skill-tree">
          <ul>
            {skills.map((node) => (
              <SkillNode key={node.id} node={node} onSelect={handleSelectQuiz} />
            ))}
          </ul>
        </div>
      ) : null}
      </div>
    </PageTransition>
  );
};

export default SkillTree;
