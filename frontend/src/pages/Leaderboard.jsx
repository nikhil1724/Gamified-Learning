import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import PageTransition from "../components/PageTransition";
import { SkeletonTable } from "../components/Skeletons";

const medalByRank = {
  1: "🥇",
  2: "🥈",
  3: "🥉",
};

const Leaderboard = () => {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        const response = await api.get("/leaderboard");
        setRows(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load leaderboard.");
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  const currentUserId = user?.id;

  const leaderboardRows = useMemo(
    () =>
      rows.map((entry) => ({
        ...entry,
        isCurrentUser: currentUserId && entry.id === currentUserId,
      })),
    [rows, currentUserId]
  );

  return (
    <PageTransition>
      <div className="container py-5">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2">
        <div>
          <h1 className="mb-2">Leaderboard</h1>
          <p className="text-muted mb-0">
            See top learners and challenge your friends.
          </p>
        </div>
      </div>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      {loading ? <SkeletonTable rows={5} cols={5} /> : null}

      {!loading && leaderboardRows.length === 0 ? (
        <div className="alert alert-info">No leaderboard data yet.</div>
      ) : null}

      {!loading && leaderboardRows.length > 0 ? (
        <div className="table-responsive shadow-sm rounded">
          <table className="table table-striped table-hover align-middle mb-0">
            <thead className="table-dark">
              <tr>
                <th scope="col">Rank</th>
                <th scope="col">Student Name</th>
                <th scope="col">Level</th>
                <th scope="col">XP Points</th>
                <th scope="col">Coins</th>
              </tr>
            </thead>
            <tbody>
              {leaderboardRows.map((entry) => (
                <tr
                  key={entry.id}
                  className={entry.isCurrentUser ? "table-primary" : ""}
                >
                  <td>
                    <span className="fw-semibold">{entry.rank}</span>{" "}
                    <span className="ms-1">{medalByRank[entry.rank]}</span>
                  </td>
                  <td>
                    <span className="fw-semibold">{entry.name}</span>
                    {entry.isCurrentUser ? (
                      <span className="badge text-bg-primary ms-2">You</span>
                    ) : null}
                  </td>
                  <td>{entry.level}</td>
                  <td>{entry.xp_points}</td>
                  <td>{entry.coins}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      </div>
    </PageTransition>
  );
};

export default Leaderboard;
