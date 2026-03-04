import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import PageTransition from "../components/PageTransition";

const Rewards = () => {
  const { isAuthenticated } = useAuth();
  const [rewards, setRewards] = useState([]);
  const [userRewards, setUserRewards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRewards = async () => {
      try {
        setLoading(true);
        const allRewardsRes = await api.get("/rewards");
        setRewards(allRewardsRes.data || []);

        if (isAuthenticated) {
          try {
            const userRewardsRes = await api.get("/user/rewards");
            setUserRewards(userRewardsRes.data || []);
          } catch {
            setUserRewards([]);
          }
        } else {
          setUserRewards([]);
        }
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load rewards.");
      } finally {
        setLoading(false);
      }
    };

    fetchRewards();
  }, [isAuthenticated]);

  const unlockedIds = useMemo(
    () => new Set(userRewards.map((reward) => reward.id)),
    [userRewards]
  );

  const renderBadgeCard = (badge, isUnlocked) => (
    <div className="col-12 col-md-6 col-lg-4" key={badge.id}>
      <div
        className={`card h-100 shadow-sm border-0 ${
          isUnlocked ? "bg-success bg-opacity-10" : "bg-light"
        }`}
      >
        <div className="card-body d-flex flex-column">
          <div className="d-flex align-items-center justify-content-between mb-3">
            <span className="badge text-bg-dark">Badge</span>
            <span
              className={`badge ${
                isUnlocked ? "text-bg-success" : "text-bg-secondary"
              }`}
            >
              {isUnlocked ? "Unlocked" : "Locked"}
            </span>
          </div>
          <h5 className="card-title">{badge.badge_name}</h5>
          <p className="card-text text-muted">{badge.description}</p>
          <div className="mt-auto">
            <span className="badge text-bg-primary">
              XP Required: {badge.xp_required}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <PageTransition>
      <div className="container py-5">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2">
        <div>
          <h1 className="mb-2">Rewards & Badges</h1>
          <p className="text-muted mb-0">
            Track your achievements and unlock new badges.
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

      {!loading ? (
        <>
          <section className="mb-5">
            <h4 className="mb-3">All Available Badges</h4>
            <div className="row g-4">
              {rewards.length === 0 ? (
                <div className="col-12">
                  <div className="alert alert-info">No badges available yet.</div>
                </div>
              ) : (
                rewards.map((badge) => renderBadgeCard(badge, unlockedIds.has(badge.id)))
              )}
            </div>
          </section>

          <section>
            <h4 className="mb-3">Your Unlocked Badges</h4>
            {!isAuthenticated ? (
              <div className="alert alert-warning">
                Please log in to view your unlocked badges.
              </div>
            ) : (
              <div className="row g-4">
                {userRewards.length === 0 ? (
                  <div className="col-12">
                    <div className="alert alert-info">
                      No badges unlocked yet. Complete quizzes to earn rewards!
                    </div>
                  </div>
                ) : (
                  userRewards.map((badge) => renderBadgeCard(badge, true))
                )}
              </div>
            )}
          </section>
        </>
      ) : null}
      </div>
    </PageTransition>
  );
};

export default Rewards;
