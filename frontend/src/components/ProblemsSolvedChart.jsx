import { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import api from "../services/api";
import "./AnalyticsCharts.css";

const ProblemsSolvedChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalSolved, setTotalSolved] = useState(0);
  const [totalSubmissions, setTotalSubmissions] = useState(0);

  useEffect(() => {
    const fetchProblemsSolved = async () => {
      try {
        setLoading(true);
        const response = await api.get("/analytics/problems-solved");
        setData(response.data.data || []);
        setTotalSolved(response.data.total_solved || 0);
        setTotalSubmissions(response.data.total_submissions || 0);
      } catch (err) {
        setError("Failed to load problems data");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProblemsSolved();
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;

    const data = payload[0]?.payload;
    return (
      <div className="chart-tooltip">
        <p className="tooltip-date">{data.date}</p>
        <p className="tooltip-solved">✓ Solved: <strong>{data.solved}</strong></p>
        <p className="tooltip-failed">✗ Failed: <strong>{data.failed}</strong></p>
        <p className="tooltip-total">Total: {data.total}</p>
      </div>
    );
  };

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">Problems Solved</h3>
        <div className="chart-stats">
          <div className="stat-item">
            <span className="stat-label">Total Solved</span>
            <span className="stat-value">{totalSolved}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Submissions</span>
            <span className="stat-value">{totalSubmissions}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="chart-loading">Loading chart...</div>
      ) : error ? (
        <div className="chart-error">{error}</div>
      ) : data.length === 0 ? (
        <div className="chart-empty">No problems solved yet. Start solving some problems!</div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="solvedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#16a34a" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#16a34a" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="failedGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                style={{ fontSize: "12px", fill: "#666" }}
                tick={{ dy: 5 }}
              />
              <YAxis style={{ fontSize: "12px", fill: "#666" }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="solved"
                stroke="#16a34a"
                fillOpacity={1}
                fill="url(#solvedGradient)"
                name="Solved"
              />
              <Area
                type="monotone"
                dataKey="failed"
                stroke="#ef4444"
                fillOpacity={1}
                fill="url(#failedGradient)"
                name="Failed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default ProblemsSolvedChart;
