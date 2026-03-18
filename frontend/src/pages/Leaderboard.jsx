import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { getLeaderboardSocket } from "../services/leaderboardSocket";
import api from "../services/api";
import PageTransition from "../components/PageTransition";
import { SkeletonTable } from "../components/Skeletons";
import "./Leaderboard.css";

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

  const applyLeaderboard = (incomingRows) => {
    if (!Array.isArray(incomingRows)) {
      return;
    }

    setRows((previousRows) => {
      const previousRankById = new Map(previousRows.map((entry) => [entry.id, entry.rank]));

      return incomingRows.map((entry) => {
        const previousRank = previousRankById.get(entry.id);
        const rankDelta = typeof previousRank === "number" ? previousRank - entry.rank : 0;

        return {
          ...entry,
          rank_delta: rankDelta,
        };
      });
    });
  };

  const applyLeaderboardDelta = (payload) => {
    const changed = Array.isArray(payload?.changed) ? payload.changed : [];
    const removedIds = Array.isArray(payload?.removed_ids) ? payload.removed_ids : [];

    if (changed.length === 0 && removedIds.length === 0) {
      return;
    }

    setRows((previousRows) => {
      const previousRankById = new Map(previousRows.map((entry) => [entry.id, entry.rank]));
      const mergedById = new Map(previousRows.map((entry) => [entry.id, { ...entry }]));

      removedIds.forEach((id) => {
        mergedById.delete(id);
      });

      changed.forEach((entry) => {
        mergedById.set(entry.id, { ...entry });
      });

      return Array.from(mergedById.values())
        .sort((a, b) => a.rank - b.rank)
        .map((entry) => {
          const previousRank = previousRankById.get(entry.id);
          const rankDelta = typeof previousRank === "number" ? previousRank - entry.rank : 0;

          return {
            ...entry,
            rank_delta: rankDelta,
          };
        });
    });
  };

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        const response = await api.get("/leaderboard");
        applyLeaderboard(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load leaderboard.");
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();

    const pollingInterval = setInterval(fetchLeaderboard, 30000);
    return () => clearInterval(pollingInterval);
  }, []);

  useEffect(() => {
    const socket = getLeaderboardSocket();

    const onConnect = () => {
      socket.emit("leaderboard:subscribe");
    };

    const onLeaderboardUpdate = (payload) => {
      if (Array.isArray(payload)) {
        applyLeaderboard(payload);
      } else if (payload?.mode === "full") {
        applyLeaderboard(payload.rows || []);
      } else if (payload?.mode === "delta") {
        applyLeaderboardDelta(payload);
      }
      setError("");
    };

    socket.on("connect", onConnect);
    socket.on("leaderboard:update", onLeaderboardUpdate);

    if (socket.connected) {
      socket.emit("leaderboard:subscribe");
    }

    return () => {
      socket.off("connect", onConnect);
      socket.off("leaderboard:update", onLeaderboardUpdate);
    };
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
                  className={`${entry.isCurrentUser ? "table-primary" : ""} ${
                    entry.rank_delta > 0
                      ? "table-row-rank-up"
                      : entry.rank_delta < 0
                        ? "table-row-rank-down"
                        : ""
                  }`}
                >
                  <td>
                    <span className="leaderboard-rank-cell">
                      <span className="fw-semibold">{entry.rank}</span>
                      <span>{medalByRank[entry.rank]}</span>
                      <span
                        className={`rank-delta ${
                          entry.rank_delta > 0
                            ? "rank-delta--up"
                            : entry.rank_delta < 0
                              ? "rank-delta--down"
                              : "rank-delta--same"
                        }`}
                        title={
                          entry.rank_delta > 0
                            ? "Rank moved up"
                            : entry.rank_delta < 0
                              ? "Rank moved down"
                              : "Rank unchanged"
                        }
                      >
                        {entry.rank_delta > 0
                          ? `↑${entry.rank_delta}`
                          : entry.rank_delta < 0
                            ? `↓${Math.abs(entry.rank_delta)}`
                            : "-"}
                      </span>
                    </span>
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
