import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import PageTransition from "../components/PageTransition";
import { publicApi } from "../services/api";

const Home = () => {
  const [stats, setStats] = useState({ students: 0, problems: 0, courses: 0 });
  const [leaderPreview, setLeaderPreview] = useState([]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const [leaderboardRes, problemsRes, coursesRes] = await Promise.all([
          publicApi.get("/leaderboard"),
          publicApi.get("/problems"),
          publicApi.get("/courses"),
        ]);

        const leaderboardRows = Array.isArray(leaderboardRes.data)
          ? leaderboardRes.data
          : [];
        const students = leaderboardRows.length;
        const problems = problemsRes.data?.data?.length || 0;
        const courses = Array.isArray(coursesRes.data) ? coursesRes.data.length : 0;

        setStats({
          students,
          problems,
          courses,
        });
        setLeaderPreview(leaderboardRows.slice(0, 3));
      } catch {
        setStats({ students: 500, problems: 20, courses: 10 });
        setLeaderPreview([]);
      }
    };

    fetchSummary();
  }, []);

  const features = useMemo(
    () => [
      { icon: "📚", title: "Learn", description: "Structured courses from basics to advanced." },
      { icon: "🧠", title: "Practice", description: "LeetCode-style coding and quiz practice." },
      { icon: "⚡", title: "Earn XP", description: "Gain XP, level up, unlock badges and rewards." },
      { icon: "🏆", title: "Compete", description: "Climb global leaderboards and track rank movement." },
    ],
    []
  );

  const steps = useMemo(
    () => [
      {
        title: "Choose a Learning Track",
        description: "Start with Python, Java, DSA, Web, or DBMS based on your goals.",
      },
      {
        title: "Solve Quizzes and Problems",
        description: "Complete timed quizzes and coding challenges with instant feedback.",
      },
      {
        title: "Earn, Level Up, and Lead",
        description: "Collect XP and badges while moving up the leaderboard.",
      },
    ],
    []
  );

  const statCards = [
    { label: "Active Students", value: stats.students || 500 },
    { label: "Practice Problems", value: stats.problems || 20 },
    { label: "Courses", value: stats.courses || 10 },
  ];

  return (
    <PageTransition>
      <div className="min-h-screen bg-slate-950 text-slate-100 font-display">
        <section className="relative overflow-hidden border-b border-white/10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_22%,rgba(59,130,246,.35),transparent_45%),radial-gradient(circle_at_85%_0%,rgba(244,63,94,.22),transparent_40%),linear-gradient(135deg,#0f172a_20%,#172554_100%)]" />
          <div className="relative mx-auto max-w-6xl px-5 py-24 md:py-28">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
              <span className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-blue-100 backdrop-blur">
                Gamified Digital Learning Platform
              </span>
              <h1 className="mt-6 max-w-4xl text-4xl font-extrabold leading-tight text-white md:text-6xl">
                Learn Like Coursera. Practice Like LeetCode. Progress Like Duolingo.
              </h1>
              <p className="mt-5 max-w-2xl text-base text-slate-200 md:text-lg">
                A complete student engagement platform with structured learning, coding arenas, XP rewards,
                badges, streaks, analytics, and real-time leaderboard updates.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/register" className="rounded-xl bg-white px-6 py-3 text-sm font-bold text-slate-900 shadow-lg transition hover:-translate-y-1">
                  Start Learning Free
                </Link>
                <Link to="/login" className="rounded-xl border border-white/30 bg-white/5 px-6 py-3 text-sm font-bold text-white backdrop-blur transition hover:bg-white/10">
                  Explore Demo
                </Link>
              </div>
              <div className="mt-7 inline-flex items-center gap-2 rounded-xl border border-emerald-300/40 bg-emerald-500/20 px-4 py-2 text-sm font-semibold text-emerald-100">
                <span>⚡</span>
                <span>+50 XP average gained per daily active learner</span>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-16">
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="text-3xl font-extrabold text-white md:text-4xl">Core Features</h2>
          </motion.div>
          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-glass backdrop-blur"
              >
                <div className="text-3xl">{feature.icon}</div>
                <h3 className="mt-3 text-xl font-semibold text-white">{feature.title}</h3>
                <p className="mt-2 text-sm text-slate-300">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="border-y border-white/10 bg-slate-900/60">
          <div className="mx-auto max-w-6xl px-5 py-16">
            <h2 className="text-3xl font-extrabold text-white md:text-4xl">How It Works</h2>
            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {steps.map((step, index) => (
                <div key={step.title} className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/80 to-slate-800/60 p-6">
                  <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20 text-sm font-bold text-blue-100">
                    {index + 1}
                  </div>
                  <h3 className="mt-3 text-lg font-bold text-white">{step.title}</h3>
                  <p className="mt-2 text-sm text-slate-300">{step.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-16">
          <div className="grid gap-4 md:grid-cols-3">
            {statCards.map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center">
                <div className="text-4xl font-extrabold text-white">{item.value}+</div>
                <div className="mt-2 text-sm text-slate-300">{item.label}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-16">
          <h2 className="text-3xl font-extrabold text-white md:text-4xl">Leaderboard Preview</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {(leaderPreview.length ? leaderPreview : [
              { rank: 1, name: "Demo User 1", xp_points: 1200, level: 5 },
              { rank: 2, name: "Demo User 2", xp_points: 980, level: 4 },
              { rank: 3, name: "Demo User 3", xp_points: 840, level: 4 },
            ]).map((entry) => (
              <div key={`${entry.rank}-${entry.name}`} className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                <div className="text-2xl">{entry.rank === 1 ? "🥇" : entry.rank === 2 ? "🥈" : "🥉"}</div>
                <div className="mt-2 text-lg font-semibold text-white">{entry.name}</div>
                <div className="mt-1 text-sm text-slate-300">Level {entry.level} • {entry.xp_points} XP</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-20">
          <div className="rounded-3xl border border-blue-200/20 bg-[linear-gradient(135deg,#1e3a8a_0%,#172554_45%,#312e81_100%)] p-8 text-center shadow-glass md:p-12">
            <h2 className="text-3xl font-extrabold text-white md:text-4xl">Ready To Launch Your Learning Streak?</h2>
            <p className="mx-auto mt-3 max-w-2xl text-sm text-blue-100 md:text-base">
              Join the platform, solve your first quiz, earn your first badge, and show your growth on the leaderboard.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Link to="/register" className="rounded-xl bg-white px-6 py-3 text-sm font-bold text-slate-900 transition hover:-translate-y-1">
                Create Account
              </Link>
              <Link to="/role-select" className="rounded-xl border border-white/30 bg-transparent px-6 py-3 text-sm font-bold text-white transition hover:bg-white/10">
                Choose Role
              </Link>
            </div>
          </div>
        </section>
      </div>
    </PageTransition>
  );
};

export default Home;
