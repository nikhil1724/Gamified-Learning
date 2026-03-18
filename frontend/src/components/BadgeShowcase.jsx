import "./BadgeShowcase.css";

const BadgeShowcase = ({ badges = [] }) => {
  if (!badges.length) {
    return (
      <div className="badge-showcase badge-showcase--empty">
        <h5 className="mb-2">Achievements</h5>
        <p className="mb-0">Complete activities to unlock your first badge.</p>
      </div>
    );
  }

  return (
    <div className="badge-showcase">
      <h5 className="mb-3">Achievements</h5>
      <div className="badge-grid" role="list" aria-label="User achievements">
        {badges.map((badge) => (
          <div
            key={`${badge.id}-${badge.earned_at}`}
            className="badge-chip"
            role="listitem"
            title={`${badge.name}: ${badge.description}`}
          >
            <span className="badge-chip__icon" aria-hidden="true">
              {badge.icon || "🏅"}
            </span>
            <span className="badge-chip__name">{badge.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BadgeShowcase;
