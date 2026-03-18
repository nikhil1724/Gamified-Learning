import { useEffect } from "react";

import "./AchievementToast.css";

const AchievementToast = ({ items = [], onDismiss }) => {
  useEffect(() => {
    if (!items.length) {
      return undefined;
    }

    const timers = items.map((item) =>
      setTimeout(() => {
        onDismiss(item.id);
      }, 4200)
    );

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [items, onDismiss]);

  if (!items.length) {
    return null;
  }

  return (
    <div className="achievement-toast-stack" aria-live="polite" aria-atomic="false">
      {items.map((item) => (
        <div key={item.id} className="achievement-toast">
          <span className="achievement-toast__icon" aria-hidden="true">
            {item.icon || "🏅"}
          </span>
          <div className="achievement-toast__content">
            <strong>{item.title || "Achievement Unlocked"}</strong>
            <p className="mb-0">{item.message}</p>
          </div>
          <button
            type="button"
            className="achievement-toast__close"
            onClick={() => onDismiss(item.id)}
            aria-label="Dismiss achievement"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};

export default AchievementToast;
