import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import api from "../services/api";
import PageTransition from "../components/PageTransition";

const InstructorAnalytics = () => {
  const { courseId } = useParams();
  const [summary, setSummary] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError("");

        const [summaryRes, studentsRes] = await Promise.all([
          api.get(`/instructor/analytics/${courseId}`),
          api.get(`/teacher/course/${courseId}/students`),
        ]);

        setSummary(summaryRes.data || null);
        setStudents(studentsRes.data?.students || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load instructor analytics.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [courseId]);

  const progressChartData = useMemo(() => {
    if (!summary) return [];
    return [
      {
        metric: "Completion",
        value: Number(summary.completion_rate || 0),
      },
    ];
  }, [summary]);

  const quizScoreChartData = useMemo(() => {
    if (!summary) return [];
    return [
      {
        metric: "Avg Quiz Score",
        value: Number(summary.average_quiz_score || 0),
      },
    ];
  }, [summary]);

  const studentActivityChartData = useMemo(() => {
    return students
      .slice(0, 8)
      .map((student) => ({
        name: student.name,
        progress: Number(student.progress_percentage || 0),
      }));
  }, [students]);

  const pieData = useMemo(() => {
    const done = Number(summary?.completion_rate || 0);
    return [
      { name: "Completed", value: done },
      { name: "Remaining", value: Math.max(0, 100 - done) },
    ];
  }, [summary]);

  return (
    <PageTransition>
      <div className="container py-5">
        <div className="d-flex justify-content-between align-items-start mb-4 gap-3 flex-wrap">
          <div>
            <h2 className="mb-1">Instructor Analytics</h2>
            <p className="text-muted mb-0">Course ID: {courseId}</p>
          </div>
          <Link to={`/teacher/course/${courseId}/analytics`} className="btn btn-outline-primary btn-sm">
            Detailed Analytics →
          </Link>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        {loading ? (
          <div className="text-muted">Loading analytics...</div>
        ) : summary ? (
          <>
            <div className="row g-3 mb-4">
              <div className="col-md-4">
                <div className="card border-0 shadow-sm">
                  <div className="card-body">
                    <div className="text-muted small">Students Enrolled</div>
                    <div className="fs-3 fw-bold">{summary.students_enrolled ?? 0}</div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card border-0 shadow-sm">
                  <div className="card-body">
                    <div className="text-muted small">Average Quiz Score</div>
                    <div className="fs-3 fw-bold">{summary.average_quiz_score ?? 0}%</div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card border-0 shadow-sm">
                  <div className="card-body">
                    <div className="text-muted small">Completion Rate</div>
                    <div className="fs-3 fw-bold">{summary.completion_rate ?? 0}%</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="row g-4">
              <div className="col-lg-6">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body">
                    <h6 className="mb-3">Progress Chart</h6>
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={progressChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="metric" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="col-lg-6">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body">
                    <h6 className="mb-3">Quiz Score Chart</h6>
                    <ResponsiveContainer width="100%" height={260}>
                      <LineChart data={quizScoreChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="metric" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Line type="monotone" dataKey="value" stroke="#16a34a" strokeWidth={3} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="col-lg-6">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body">
                    <h6 className="mb-3">Student Activity Chart</h6>
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={studentActivityChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" hide />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Bar dataKey="progress" fill="#f59e0b" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="col-lg-6">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body">
                    <h6 className="mb-3">Completion Split</h6>
                    <ResponsiveContainer width="100%" height={260}>
                      <PieChart>
                        <Tooltip />
                        <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} fill="#8b5cf6" />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-muted">No analytics data available.</div>
        )}
      </div>
    </PageTransition>
  );
};

export default InstructorAnalytics;
