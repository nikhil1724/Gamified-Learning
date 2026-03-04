import { useEffect, useMemo, useState } from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { useAuth } from "../context/AuthContext";
import api, { publicApi } from "../services/api";
import PageTransition from "../components/PageTransition";
import { SkeletonCard, SkeletonStats } from "../components/Skeletons";
import XPProgressChart from "../components/XPProgressChart";
import QuizScoresChart from "../components/QuizScoresChart";
import ProblemsSolvedChart from "../components/ProblemsSolvedChart";
import "./Dashboard.css";

const Dashboard = () => {
  const { isAuthenticated, user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [skills, setSkills] = useState([]);
  const [dailyStatus, setDailyStatus] = useState(null);
  const [dailyChallenge, setDailyChallenge] = useState(null);
  const [dailyLoading, setDailyLoading] = useState(false);
  const [dailyError, setDailyError] = useState("");
  const [dailyCompleting, setDailyCompleting] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [userBadges, setUserBadges] = useState([]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        if (!isAuthenticated) {
          setError("Please log in to view recommendations.");
          return;
        }
        setLoading(true);
        const response = await api.get("/recommendations");
        setData(response.data);
      } catch (err) {
        const message =
          err?.response?.data?.error ||
          err?.response?.data?.msg ||
          "Failed to load recommendations.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated]);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await publicApi.get("/leaderboard");
        setLeaderboard(response.data || []);
      } catch {
        setLeaderboard([]);
      }
    };

    fetchLeaderboard();
  }, []);

  useEffect(() => {
    const fetchBadges = async () => {
      if (!isAuthenticated) {
        setUserBadges([]);
        return;
      }

      try {
        const response = await api.get("/user/rewards");
        setUserBadges(response.data || []);
      } catch {
        setUserBadges([]);
      }
    };

    fetchBadges();
  }, [isAuthenticated]);

  useEffect(() => {
    const fetchDailyStatus = async () => {
      if (!isAuthenticated) {
        setDailyStatus(null);
        return;
      }

      try {
        const response = await api.get("/daily-challenge/status");
        setDailyStatus(response.data);
      } catch {
        setDailyStatus(null);
      }
    };

    fetchDailyStatus();
  }, [isAuthenticated]);

  useEffect(() => {
    const fetchDailyChallenge = async () => {
      try {
        setDailyLoading(true);
        setDailyError("");
        const response = await publicApi.get("/daily-challenge");
        setDailyChallenge(response.data);
      } catch (err) {
        setDailyChallenge(null);
        setDailyError(err?.response?.data?.error || "No daily mission available.");
      } finally {
        setDailyLoading(false);
      }
    };

    fetchDailyChallenge();
  }, []);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await publicApi.get("/skills");
        setSkills(response.data || []);
      } catch {
        setSkills([]);
      }
    };

    fetchSkills();
  }, []);

  const motivationalMessage = useMemo(() => {
    if (!data?.performance_summary) {
      return "Keep learning and unlock new achievements!";
    }

    const accuracy = data.performance_summary.accuracy_percentage;
    if (accuracy > 80) {
      return "Great progress! Try harder challenges.";
    }
    if (accuracy < 50) {
      return "Let’s revise fundamentals and build confidence.";
    }
    return "Nice work! Keep pushing forward.";
  }, [data]);

  const xpProgress = useMemo(() => {
    const xpPoints = user?.xp_points || 0;
    const level = user?.level || 1;
    const nextLevelXp = level * 100;
    const progress = Math.min((xpPoints / nextLevelXp) * 100, 100);
    return { xpPoints, level, nextLevelXp, progress };
  }, [user]);

  const skillStats = useMemo(() => {
    const flatten = (nodes) =>
      nodes.flatMap((node) => [node, ...(node.children ? flatten(node.children) : [])]);
    const allSkills = flatten(skills);
    const total = allSkills.length || 0;
    const unlocked = allSkills.filter((skill) => skill.unlocked).length;
    const progress = total ? Math.round((unlocked / total) * 100) : 0;
    return { total, unlocked, progress };
  }, [skills]);

  const currentRank = useMemo(() => {
    if (!user?.id) {
      return "-";
    }

    const entry = leaderboard.find((item) => item.id === user.id);
    return entry ? `#${entry.rank}` : "-";
  }, [leaderboard, user]);

  const totalQuizzesCompleted = data?.performance_summary?.total_attempts ?? 0;
  const accuracyPercent = data?.performance_summary?.accuracy_percentage ?? 0;

  const topicPerformance = useMemo(() => {
    const topicAccuracy = data?.performance_summary?.topic_accuracy || [];
    return topicAccuracy.map((entry) => ({
      topic: entry.topic,
      accuracy: entry.accuracy,
      correct: entry.correct,
      total: entry.total_questions,
    }));
  }, [data]);

  const RadarTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) {
      return null;
    }

    const item = payload[0]?.payload;
    return (
      <div className="analytics-tooltip">
        <div className="fw-semibold mb-1">{item.topic}</div>
        <div className="small text-muted">Accuracy: {item.accuracy}%</div>
        <div className="small text-muted">
          {item.correct}/{item.total} correct
        </div>
      </div>
    );
  };

  const handleDailyComplete = async () => {
    if (!isAuthenticated) {
      setDailyError("Please log in to complete missions.");
      return;
    }

    try {
      setDailyCompleting(true);
      const response = await api.post("/daily-challenge/complete");
      setDailyStatus((prev) => ({
        ...prev,
        completed_today: true,
        daily_streak: response.data?.daily_streak ?? prev?.daily_streak ?? 0,
        bonus_xp: response.data?.bonus_xp ?? prev?.bonus_xp ?? 0,
      }));
    } catch (err) {
      setDailyError(
        err?.response?.data?.error ||
          err?.response?.data?.msg ||
          "Failed to complete the daily mission."
      );
    } finally {
      setDailyCompleting(false);
    }
  };

  return (
    <PageTransition>
      <div className="container py-5">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2">
        <div>
          <h1 className="mb-2">Dashboard</h1>
          <p className="text-muted mb-0">
            Track your progress and get personalized recommendations.
          </p>
        </div>
        <span className="badge text-bg-primary fs-6">
          Suggested Difficulty: {data?.difficulty_suggestion || "-"}
        </span>
      </div>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      {loading && !data ? (
        <div className="row g-4">
          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <SkeletonCard />
            </div>
          </div>
          <div className="col-12 col-lg-8">
            <div className="rpg-card">
              <SkeletonCard />
            </div>
          </div>
          <div className="col-12">
            <SkeletonStats />
          </div>
          <div className="col-12 col-lg-4">
            <SkeletonCard />
          </div>
          <div className="col-12 col-lg-4">
            <SkeletonCard />
          </div>
          <div className="col-12 col-lg-4">
            <SkeletonCard />
          </div>
        </div>
      ) : null}

      {!loading && data ? (
        <div className="row g-4">
          <div className="col-12 col-lg-4">
            <div className="rpg-card profile-card">
              <div className="profile-header">
                <div className="avatar-circle">
                  {user?.name ? user.name.charAt(0).toUpperCase() : "G"}
                </div>
                <div>
                  <h4 className="mb-1">{user?.name || "Adventurer"}</h4>
                  <span className="level-badge">Lv. {xpProgress.level}</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="text-muted">XP</span>
                  <span className="text-muted">
                    {xpProgress.xpPoints}/{xpProgress.nextLevelXp}
                  </span>
                </div>
                <div className="xp-bar">
                  <div className="xp-bar__fill" style={{ width: `${xpProgress.progress}%` }} />
                </div>
              </div>
              <div className="coins-display mt-3">
                <span className="coins-icon">🪙</span>
                <span>{user?.coins ?? 0} Coins</span>
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-8">
            <div className="rpg-card status-card">
              <h5 className="mb-2">Status Message</h5>
              <p className="mb-0 text-muted">{motivationalMessage}</p>
              <div className="status-glow" />
            </div>
          </div>

          <div className="col-12">
            {loading ? (
              <SkeletonStats />
            ) : (
              <div className="row g-3">
                <div className="col-6 col-lg-3">
                  <div className="rpg-card stat-card">
                    <h6>Total Quizzes</h6>
                    <p className="stat-value">{totalQuizzesCompleted}</p>
                  </div>
                </div>
                <div className="col-6 col-lg-3">
                  <div className="rpg-card stat-card">
                    <h6>Accuracy</h6>
                    <p className="stat-value">{accuracyPercent}%</p>
                  </div>
                </div>
                <div className="col-6 col-lg-3">
                  <div className="rpg-card stat-card">
                    <h6>Current Rank</h6>
                    <p className="stat-value">{currentRank}</p>
                  </div>
                </div>
                <div className="col-6 col-lg-3">
                  <div className="rpg-card stat-card">
                    <h6>Badges</h6>
                    <p className="stat-value">{userBadges.length}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <h5 className="mb-3">Performance Summary</h5>
              <ul className="list-group list-group-flush">
                <li className="list-group-item d-flex justify-content-between">
                  <span>Accuracy</span>
                  <strong>{accuracyPercent}%</strong>
                </li>
                <li className="list-group-item d-flex justify-content-between">
                  <span>Average Score</span>
                  <strong>{data.performance_summary.average_score}</strong>
                </li>
                <li className="list-group-item d-flex justify-content-between">
                  <span>Trend</span>
                  <strong className="text-capitalize">
                    {data.performance_summary.trend}
                  </strong>
                </li>
              </ul>
              <div className="mt-3">
                <div className="chart-bar">
                  <div className="chart-fill" style={{ width: `${accuracyPercent}%` }} />
                </div>
                <small className="text-muted">Accuracy trend</small>
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="rpg-card mission-board">
              <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                <div>
                  <h5 className="mb-1">Daily Mission Board</h5>
                  <p className="text-muted mb-0">
                    Complete quests to keep your streak alive.
                  </p>
                </div>
                <div className="streak-counter">
                  <span className="fire-icon">🔥</span>
                  <span className="fw-semibold">
                    {dailyStatus?.daily_streak ?? 0} day streak
                  </span>
                </div>
              </div>

              {dailyError ? (
                <div className="alert alert-warning mb-3">{dailyError}</div>
              ) : null}

              {dailyLoading ? (
                <div className="mission-skeleton" />
              ) : dailyChallenge?.quiz ? (
                <div className="mission-grid">
                  <div className="mission-card">
                    <div className="mission-header">
                      <span className="mission-tag">Daily Quest</span>
                      <span className="mission-reward">
                        +{dailyStatus?.bonus_xp ?? 50} XP
                      </span>
                    </div>
                    <h6 className="mb-2">{dailyChallenge.quiz.title}</h6>
                    <p className="text-muted small mb-3">
                      {dailyChallenge.quiz.topic} • {dailyChallenge.quiz.difficulty}
                    </p>
                    <div className="mission-progress">
                      <div className="d-flex justify-content-between small text-muted mb-1">
                        <span>Progress</span>
                        <span>
                          {dailyStatus?.completed_today ? "Completed" : "0%"}
                        </span>
                      </div>
                      <div className="progress" style={{ height: "10px" }}>
                        <div
                          className={`progress-bar ${
                            dailyStatus?.completed_today ? "bg-success" : "bg-info"
                          }`}
                          role="progressbar"
                          style={{ width: dailyStatus?.completed_today ? "100%" : "0%" }}
                          aria-valuenow={dailyStatus?.completed_today ? 100 : 0}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      className="btn btn-outline-primary w-100 mt-3"
                      onClick={handleDailyComplete}
                      disabled={dailyStatus?.completed_today || dailyCompleting}
                    >
                      {dailyStatus?.completed_today
                        ? "Mission Completed"
                        : dailyCompleting
                        ? "Completing..."
                        : "Mark as Complete"}
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-muted mb-0">No missions available today.</p>
              )}
            </div>
          </div>

          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <h5 className="mb-3">Recommended Quizzes</h5>
              {loading ? (
                <SkeletonCard />
              ) : data.recommended_quizzes.length === 0 ? (
                <p className="text-muted mb-0">No quiz recommendations yet.</p>
              ) : (
                <ul className="list-group list-group-flush">
                  {data.recommended_quizzes.map((quiz) => (
                    <li key={quiz.id} className="list-group-item">
                      <div className="fw-semibold">{quiz.title}</div>
                      <small className="text-muted">
                        {quiz.topic} • {quiz.difficulty}
                      </small>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <h5 className="mb-3">Recommended Skills</h5>
              {loading ? (
                <SkeletonCard />
              ) : data.recommended_skills.length === 0 ? (
                <p className="text-muted mb-0">No skill recommendations yet.</p>
              ) : (
                <ul className="list-group list-group-flush">
                  {data.recommended_skills.map((skill) => (
                    <li key={skill.id} className="list-group-item">
                      <div className="fw-semibold">{skill.skill_name}</div>
                      <small className="text-muted">{skill.description}</small>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="col-12 col-lg-8">
            <div className="rpg-card">
              <div className="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
                <h5 className="mb-0">Learning Analytics</h5>
                <span className="badge text-bg-info">Topic Accuracy</span>
              </div>
              {loading ? (
                <div className="analytics-skeleton" />
              ) : topicPerformance.length === 0 ? (
                <p className="text-muted mb-0">
                  Complete more quizzes to unlock topic analytics.
                </p>
              ) : (
                <div className="analytics-chart">
                  <ResponsiveContainer width="100%" height={280}>
                    <RadarChart data={topicPerformance} outerRadius="78%">
                      <PolarGrid stroke="rgba(148, 163, 184, 0.45)" />
                      <PolarAngleAxis dataKey="topic" />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} />
                      <Radar
                        name="Accuracy"
                        dataKey="accuracy"
                        stroke="#0d6efd"
                        fill="rgba(13, 110, 253, 0.35)"
                        dot={{ r: 3, fill: "#0d6efd" }}
                        isAnimationActive
                      />
                      <Tooltip content={<RadarTooltip />} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>

          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <h5 className="mb-3">Skill Completion</h5>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted">Unlocked</span>
                <strong>
                  {skillStats.unlocked}/{skillStats.total}
                </strong>
              </div>
              <div className="progress" style={{ height: "10px" }}>
                <div
                  className="progress-bar bg-success"
                  role="progressbar"
                  style={{ width: `${skillStats.progress}%` }}
                  aria-valuenow={skillStats.progress}
                  aria-valuemin="0"
                  aria-valuemax="100"
                />
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-4">
            <div className="rpg-card">
              <h5 className="mb-3">Daily Streak</h5>
              <div className="d-flex align-items-center justify-content-between mb-2">
                <span className="text-muted">Current streak</span>
                <strong>{dailyStatus?.daily_streak ?? 0} days</strong>
              </div>
              <div className="progress" style={{ height: "10px" }}>
                <div
                  className="progress-bar bg-warning"
                  role="progressbar"
                  style={{ width: `${Math.min((dailyStatus?.daily_streak ?? 0) * 10, 100)}%` }}
                  aria-valuenow={dailyStatus?.daily_streak ?? 0}
                  aria-valuemin="0"
                  aria-valuemax="10"
                />
              </div>
              <small className="text-muted d-block mt-2">
                {dailyStatus?.completed_today
                  ? `Bonus claimed (+${dailyStatus.bonus_xp} XP)`
                  : "Complete today’s challenge to keep the streak alive."}
              </small>
            </div>
          </div>
          {/* Analytics Charts Section */}
          <div className="col-12">
            <h4 className="mb-4 mt-2">Your Analytics</h4>
          </div>

          <div className="col-12 col-lg-6">
            <XPProgressChart />
          </div>

          <div className="col-12 col-lg-6">
            <QuizScoresChart />
          </div>

          <div className="col-12">
            <ProblemsSolvedChart />
          </div>        </div>
      ) : null}
      </div>
    </PageTransition>
  );
};

export default Dashboard;
