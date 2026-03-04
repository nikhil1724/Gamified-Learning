import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import "./ProfileDropdown.css";

const getDashboardPath = (role) => {
  if (role === "admin") {
    return "/admin/dashboard";
  }
  if (role === "teacher") {
    return "/teacher/dashboard";
  }
  return "/my-learning";
};

const ProfileDropdown = ({ user, role, onLogout }) => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [menuStyle, setMenuStyle] = useState({});
  const menuRef = useRef(null);
  const buttonRef = useRef(null);
  const secondaryLinks = useMemo(() => {
    if (role !== "student") {
      return [];
    }
    return [
      { label: "Quiz", path: "/quiz" },
      { label: "Skill Tree", path: "/skills" },
      { label: "Leaderboard", path: "/leaderboard" },
      { label: "Rewards", path: "/rewards" },
    ];
  }, [role]);

  const initials = useMemo(() => {
    if (!user?.name) {
      return "U";
    }
    return user.name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();
  }, [user?.name]);

  const updatePosition = () => {
    const rect = buttonRef.current?.getBoundingClientRect();
    if (!rect) {
      return;
    }
    setMenuStyle({ top: rect.bottom + 10 });
  };

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, { passive: true });

    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition);
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const handleClickOutside = (event) => {
      if (menuRef.current?.contains(event.target)) {
        return;
      }
      if (buttonRef.current?.contains(event.target)) {
        return;
      }
      setIsOpen(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleNavigate = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  const handleLogout = async () => {
    setIsOpen(false);
    await onLogout();
  };

  return (
    <div className="profile-menu">
      <button
        type="button"
        className="profile-menu__button"
        onClick={() => setIsOpen((prev) => !prev)}
        ref={buttonRef}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Open profile menu"
      >
        <span className="profile-menu__avatar">{initials}</span>
      </button>

      <div
        className={`profile-menu__panel ${isOpen ? "is-open" : ""}`}
        ref={menuRef}
        style={menuStyle}
        role="menu"
        aria-hidden={!isOpen}
      >
        <div className="profile-menu__identity">
          <div className="profile-menu__name">{user?.name || "User"}</div>
          <div className="profile-menu__email">{user?.email || ""}</div>
        </div>
        <div className="profile-menu__divider" />
        <button
          type="button"
          className="profile-menu__item"
          onClick={() => handleNavigate("/profile")}
        >
          My Profile
        </button>
        <button
          type="button"
          className="profile-menu__item"
          onClick={() => handleNavigate(getDashboardPath(role))}
        >
          My Dashboard
        </button>
        <button
          type="button"
          className="profile-menu__item"
          onClick={() => handleNavigate("/settings")}
        >
          Settings
        </button>
        {secondaryLinks.length ? <div className="profile-menu__divider" /> : null}
        {secondaryLinks.map((link) => (
          <button
            key={link.path}
            type="button"
            className="profile-menu__item"
            onClick={() => handleNavigate(link.path)}
          >
            {link.label}
          </button>
        ))}
        {secondaryLinks.length ? <div className="profile-menu__divider" /> : null}
        <button
          type="button"
          className="profile-menu__item profile-menu__item--danger"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default ProfileDropdown;
