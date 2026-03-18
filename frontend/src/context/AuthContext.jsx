import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

const AuthContext = createContext(null);

const decodeJwtPayload = (jwtToken) => {
  const payloadSegment = jwtToken.split(".")[1];
  if (!payloadSegment) {
    return null;
  }

  const normalized = payloadSegment.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");

  try {
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
};

const getStoredToken = () => localStorage.getItem("token");
const getStoredUser = () => {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    localStorage.removeItem("user");
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const isTokenValid = (jwtToken) => {
    if (!jwtToken) {
      return false;
    }

    const decoded = decodeJwtPayload(jwtToken);
    if (!decoded) {
      return false;
    }

    if (!decoded.exp) {
      return true;
    }

    return Date.now() < decoded.exp * 1000;
  };

  // Load token & user from localStorage on mount
  useEffect(() => {
    const storedToken = getStoredToken();
    const storedUser = getStoredUser();

    if (isTokenValid(storedToken)) {
      setToken(storedToken);
      setUser(storedUser);
    } else {
      // Token invalid or expired.
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setToken(null);
      setUser(null);
    }

    setAuthLoading(false);
  }, []);

  // Persist token to localStorage
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  // Persist user to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const login = (accessToken, userInfo) => {
    setToken(accessToken);
    setUser(userInfo || null);
  };

  const updateUser = (nextUser) => {
    setUser(nextUser || null);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const handleLogout = () => {
      logout();
    };

    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      role: user?.role || null,
      isApproved: user?.is_approved ?? null,
      isAuthenticated: Boolean(token),
      authLoading,
      login,
      updateUser,
      logout,
    }),
    [token, user, authLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
