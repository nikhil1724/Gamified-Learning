import { useCallback, useEffect, useState } from "react";

import AchievementToast from "./AchievementToast";

const AchievementToastHost = () => {
  const [items, setItems] = useState([]);

  const onDismiss = useCallback((id) => {
    setItems((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  useEffect(() => {
    const handleAchievementEvent = (event) => {
      const badges = event?.detail?.badges;
      if (!Array.isArray(badges) || badges.length === 0) {
        return;
      }

      const now = Date.now();
      const nextItems = badges.map((badge, index) => ({
        id: `${now}-${index}`,
        icon: badge.icon,
        title: "Achievement Unlocked",
        message: `${badge.name} earned`,
      }));

      setItems((prev) => [...prev, ...nextItems]);
    };

    window.addEventListener("achievement:unlock", handleAchievementEvent);
    return () => {
      window.removeEventListener("achievement:unlock", handleAchievementEvent);
    };
  }, []);

  return <AchievementToast items={items} onDismiss={onDismiss} />;
};

export default AchievementToastHost;
