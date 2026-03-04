import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import api from "../services/api";
import "./AnalyticsCharts.css";

const XPProgressChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalXP, setTotalXP] = useState(0);
  const [level, setLevel] = useState(1);

  useEffect(() => {
    const fetchXPHistory = async () => {
      try {
        setLoading(true);
        const response = await api.get("/analytics/xp-history");
        setData(response.data.data || []);
        setTotalXP(response.data.total_xp || 0);
        setLevel(response.data.level || 1);
      } catch (err) {
        setError("Failed to load XP history");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchXPHistory();
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;

    const data = payload[0]?.payload;
    return (
      <div className="chart-tooltip">
        <p className="tooltip-date">{data.date}</p>
        <p className="tooltip-xp">XP: <strong>{data.xp}</strong></p>
        <p className="tooltip-quizzes">Quizzes: {data.quizzes}</p>
      </div>
    );
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">XP Progress</h3>
        <div className="chart-stats">
          <div className="stat-item">
            <span className="stat-label">Total XP</span>
            <span className="stat-value">{totalXP}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Level</span>
            <span className="stat-value">{level}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="chart-loading">Loading chart...</div>
      ) : error ? (
        <div className="chart-error">{error}</div>
      ) : data.length === 0 ? (
        <div className="chart-empty">No XP data available yet</div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                style={{ fontSize: "12px", fill: "#666" }}
                tick={{ dy: 5 }}
              />
              <YAxis style={{ fontSize: "12px", fill: "#666" }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="xp"
                stroke="#2563eb"
                dot={{ fill: "#2563eb", r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
                name="XP Gained"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default XPProgressChart;
