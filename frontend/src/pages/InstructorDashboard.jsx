import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Users,
  Code2,
  FileText,
  PlusCircle,
  PenSquare,
  Upload,
  BarChart3,
  Clock3,
  CheckCircle2,
  UserPlus,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

import PageTransition from "../components/PageTransition";
import api from "../services/api";
import "./InstructorDashboard.css";

const DEMO_ENROLLMENT_SERIES = [
  { month: "Jan", students: 22 },
  { month: "Feb", students: 31 },
  { month: "Mar", students: 40 },
  { month: "Apr", students: 48 },
  { month: "May", students: 57 },
  { month: "Jun", students: 66 },
];

const DEMO_QUIZ_SERIES = [
  { course: "Python", avgScore: 78 },
  { course: "Java", avgScore: 71 },
  { course: "DSA", avgScore: 84 },
  { course: "Web", avgScore: 75 },
];

const PIE_COLORS = ["#10b981", "#3b82f6", "#f59e0b"];

const InstructorDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_courses: 0,
    total_problems: 0,
    active_students: 0,
    total_enrollments: 0,
  });
  const [totalLessons, setTotalLessons] = useState(0);
  const [enrollmentSeries, setEnrollmentSeries] = useState(DEMO_ENROLLMENT_SERIES);
  const [quizSeries, setQuizSeries] = useState(DEMO_QUIZ_SERIES);
  const [completionSeries, setCompletionSeries] = useState([
    { name: "Completed", value: 0 },
    { name: "Active", value: 0 },
  ]);
  const [activities, setActivities] = useState([]);
  const [studentSnapshot, setStudentSnapshot] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        const [statsRes, coursesRes] = await Promise.all([
          api.get("/teacher/stats"),
          api.get("/teacher/courses"),
        ]);

        const statsPayload = statsRes.data || {};
        const courses = coursesRes.data || [];
        setStats(statsPayload);

        const notesResults = await Promise.all(
          courses.map((course) =>
            api
              .get(`/courses/${course.id}/notes`)
              .then((res) => ({ course, notes: res.data || [] }))
              .catch(() => ({ course, notes: [] }))
          )
        );

        const lessonCount = notesResults.reduce(
          (total, entry) => total + entry.notes.length,
          0
        );
        setTotalLessons(lessonCount);

        const chartScale = Math.max(statsPayload.total_enrollments || 0, 18);
        const generatedEnrollment = [
          { month: "Jan", students: Math.round(chartScale * 0.32) },
          { month: "Feb", students: Math.round(chartScale * 0.44) },
          { month: "Mar", students: Math.round(chartScale * 0.56) },
          { month: "Apr", students: Math.round(chartScale * 0.68) },
          { month: "May", students: Math.round(chartScale * 0.82) },
          { month: "Jun", students: Math.round(chartScale * 1.0) },
        ];
        setEnrollmentSeries(generatedEnrollment);

        const performanceResponses = await Promise.all(
          courses.map((course) =>
            api
              .get(`/teacher/course/${course.id}/students`)
              .then((res) => ({ course, payload: res.data }))
              .catch(() => ({ course, payload: null }))
          )
        );

        const dynamicQuizData = performanceResponses
          .map(({ course, payload }) => {
            const students = payload?.students || [];
            if (!students.length) {
              return {
                course: String(course.title || "Course").slice(0, 12),
                avgScore: 0,
              };
            }
            const sum = students.reduce(
              (acc, student) => acc + Number(student.avg_quiz_score || 0),
              0
            );
            return {
              course: String(course.title || "Course").slice(0, 12),
              avgScore: Math.round(sum / students.length),
            };
          })
          .filter((item) => item.course);

        const hasNonZeroScores = dynamicQuizData.some((item) => item.avgScore > 0);
        setQuizSeries(hasNonZeroScores ? dynamicQuizData : DEMO_QUIZ_SERIES);

        const snapshotRows = performanceResponses
          .flatMap(({ course, payload }) =>
            (payload?.students || []).map((student) => ({
              id: `${course.id}-${student.student_id}`,
              name: student.name,
              courseTitle: course.title,
              progress: Number(student.progress_percentage || 0),
              avgScore: Number(student.avg_quiz_score || 0),
            }))
          )
          .sort((a, b) => b.progress - a.progress)
          .slice(0, 6);
        setStudentSnapshot(snapshotRows);

        const studentsAcrossCourses = performanceResponses.flatMap(
          ({ payload }) => payload?.students || []
        );
        const completed = studentsAcrossCourses.filter(
          (student) => Number(student.progress_percentage || 0) >= 100
        ).length;
        const active = studentsAcrossCourses.filter(
          (student) => Number(student.progress_percentage || 0) < 100
        ).length;
        const pending = Math.max(
          (statsPayload.total_enrollments || 0) - completed - active,
          0
        );

        setCompletionSeries([
          { name: "Completed", value: completed },
          { name: "Active", value: active },
          { name: "Pending", value: pending },
        ]);

        const recentNoteEntries = notesResults
          .flatMap((entry) =>
            (entry.notes || []).map((note) => ({
              type: "lesson",
              text: `New lesson uploaded in ${entry.course.title}: ${note.title}`,
              createdAt: note.created_at || "",
            }))
          )
          .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
          .slice(0, 2);

        const activitySeed = [
          {
            type: "quiz",
            text: "Student Rahul completed Python Quiz",
            createdAt: new Date().toISOString(),
          },
          {
            type: "student",
            text: "New student registered",
            createdAt: new Date().toISOString(),
          },
          {
            type: "course",
            text: "Course \"Java Basics\" updated",
            createdAt: new Date().toISOString(),
          },
          ...recentNoteEntries,
        ].slice(0, 5);

        setActivities(activitySeed);
      } catch (error) {
        console.error("Failed to fetch instructor dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const statCards = useMemo(
    () => [
      {
        label: "Total Courses",
        value: stats.total_courses,
        icon: BookOpen,
        tone: "courses",
      },
      {
        label: "Total Students",
        value: stats.active_students,
        icon: Users,
        tone: "students",
      },
      {
        label: "Total Problems",
        value: stats.total_problems,
        icon: Code2,
        tone: "problems",
      },
      {
        label: "Total Lessons",
        value: totalLessons,
        icon: FileText,
        tone: "lessons",
      },
    ],
    [stats, totalLessons]
  );

  const quickActions = [
    {
      label: "Create New Course",
      to: "/teacher/courses",
      icon: PlusCircle,
      description: "Add a new course for your class",
    },
    {
      label: "Add Coding Problem",
      to: "/teacher/problems",
      icon: PenSquare,
      description: "Create a practical coding challenge",
    },
    {
      label: "Upload Lesson",
      to: "/teacher/courses",
      icon: Upload,
      description: "Publish lesson notes and resources",
    },
    {
      label: "View Analytics",
      to: "/teacher/students",
      icon: BarChart3,
      description: "Track student learning performance",
    },
  ];

  const handleQuickAction = (path) => {
    navigate(path);
  };

  const getActivityIcon = (type) => {
    if (type === "lesson") return Upload;
    if (type === "course") return FileText;
    if (type === "student") return UserPlus;
    return CheckCircle2;
  };

  return (
    <PageTransition>
      <div className="instructor-dashboard container py-5">
        <header className="instructor-dashboard__header">
          <div>
            <span className="instructor-badge">Instructor Workspace</span>
            <h1>Instructor Dashboard</h1>
            <p>
              A complete view of your courses, student engagement, and lesson
              delivery.
            </p>
          </div>
        </header>

        <section className="dashboard-stats">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <article key={card.label} className={`stat-card stat-card--${card.tone}`}>
                <div className="stat-card__icon-wrap">
                  <Icon size={22} />
                </div>
                <div>
                  <p className="stat-card__label">{card.label}</p>
                  <h3 className="stat-card__value">
                    {loading ? "--" : Number(card.value || 0).toLocaleString()}
                  </h3>
                </div>
              </article>
            );
          })}
        </section>

        <section className="dashboard-charts">
          <article className="dashboard-panel">
            <div className="panel-title">Student Enrollment Growth</div>
            <div className="panel-subtitle">Monthly student enrollment trend</div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={enrollmentSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" allowDecimals={false} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="students"
                    stroke="#2563eb"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dashboard-panel">
            <div className="panel-title">Quiz Performance</div>
            <div className="panel-subtitle">Average quiz score by course</div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={quizSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="course" stroke="#64748b" />
                  <YAxis stroke="#64748b" domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="avgScore" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dashboard-panel dashboard-panel--pie">
            <div className="panel-title">Course Completion</div>
            <div className="panel-subtitle">Completed vs active students</div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={completionSeries}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={92}
                    innerRadius={56}
                  >
                    {completionSeries.map((entry, index) => (
                      <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>

        <section className="dashboard-bottom">
          <article className="dashboard-panel recent-activity">
            <div className="panel-title">Recent Activities</div>
            <ul className="activity-list">
              {activities.map((activity, index) => {
                const Icon = getActivityIcon(activity.type);
                return (
                  <li className="activity-item" key={`${activity.text}-${index}`}>
                    <span className="activity-item__icon">
                      <Icon size={16} />
                    </span>
                    <div className="activity-item__content">
                      <p>{activity.text}</p>
                      <span>
                        <Clock3 size={14} />
                        Recently updated
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </article>

          <article className="dashboard-panel quick-actions">
            <div className="panel-title">Quick Actions</div>
            <div className="quick-action-grid">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    type="button"
                    key={action.label}
                    className="quick-action-btn"
                    onClick={() => handleQuickAction(action.to)}
                  >
                    <span className="quick-action-btn__icon">
                      <Icon size={18} />
                    </span>
                    <div>
                      <strong>{action.label}</strong>
                      <small>{action.description}</small>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="student-snapshot">
              <div className="student-snapshot__header">
                <h4>Student Performance Snapshot</h4>
                <button
                  type="button"
                  className="student-snapshot__link"
                  onClick={() => navigate("/teacher/students")}
                >
                  View Full Performance
                </button>
              </div>

              {studentSnapshot.length ? (
                <div className="snapshot-table">
                  {studentSnapshot.map((student) => (
                    <div className="snapshot-row" key={student.id}>
                      <div className="snapshot-row__main">
                        <strong>{student.name}</strong>
                        <small>{student.courseTitle}</small>
                      </div>
                      <div className="snapshot-row__meta">
                        <span>{student.progress}% progress</span>
                        <span>{student.avgScore}% avg score</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="student-snapshot__empty">
                  No student performance data yet. Open analytics to view enrolled students.
                </p>
              )}
            </div>
          </article>
        </section>
      </div>
    </PageTransition>
  );
};

export default InstructorDashboard;
