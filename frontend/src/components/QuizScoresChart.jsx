import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import api from "../services/api";
import "./AnalyticsCharts.css";

const QuizScoresChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [averageScore, setAverageScore] = useState(0);
  const [totalQuizzes, setTotalQuizzes] = useState(0);

  useEffect(() => {
    const fetchQuizScores = async () => {
      try {
        setLoading(true);
        const response = await api.get("/analytics/quiz-scores");
        setData(response.data.data || []);
        setAverageScore(response.data.average_score || 0);
        setTotalQuizzes(response.data.total_quizzes || 0);
      } catch (err) {
        setError("Failed to load quiz scores");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchQuizScores();
  }, []);

  const getBarColor = (percentage) => {
    if (percentage >= 80) return "#16a34a"; // green
    if (percentage >= 60) return "#2563eb"; // blue
    if (percentage >= 40) return "#f59e0b"; // amber
    return "#ef4444"; // red
  };

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;

    const data = payload[0]?.payload;
    return (
      <div className="chart-tooltip">
        <p className="tooltip-title">{data.full_title}</p>
        <p className="tooltip-score">Score: <strong>{data.score}/{data.total_questions}</strong></p>
        <p className="tooltip-percentage">Percentage: <strong>{data.percentage}%</strong></p>
        <p className="tooltip-date">{data.date}</p>
      </div>
    );
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">Quiz Performance</h3>
        <div className="chart-stats">
          <div className="stat-item">
            <span className="stat-label">Total Quizzes</span>
            <span className="stat-value">{totalQuizzes}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Average Score</span>
            <span className="stat-value">{averageScore.toFixed(1)}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="chart-loading">Loading chart...</div>
      ) : error ? (
        <div className="chart-error">{error}</div>
      ) : data.length === 0 ? (
        <div className="chart-empty">No quiz data available yet. Complete some quizzes to see your performance!</div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="quiz_title"
                style={{ fontSize: "11px", fill: "#666" }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis style={{ fontSize: "12px", fill: "#666" }} label={{ value: "Score (%)", angle: -90, position: "insideLeft" }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="percentage" name="Score %" fill="#2563eb">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.percentage)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default QuizScoresChart;
