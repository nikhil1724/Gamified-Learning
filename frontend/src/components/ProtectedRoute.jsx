import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const getRoleHome = (role, isApproved) => {
  if (role === "admin") {
    return "/admin/dashboard";
  }
  return role === "teacher" ? "/teacher-dashboard" : "/student-dashboard";
};

const ProtectedRoute = ({ children, allowedRoles, role: requiredRole }) => {
  const { isAuthenticated, authLoading, role, isApproved } = useAuth();
  const effectiveAllowedRoles =
    allowedRoles?.length ? allowedRoles : requiredRole ? [requiredRole] : [];

  // CRITICAL: Wait for auth state to load before rendering
  if (authLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "100vh" }}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (effectiveAllowedRoles.length && !role) {
    return <Navigate to="/login" replace />;
  }

  if (effectiveAllowedRoles.length && !effectiveAllowedRoles.includes(role)) {
    return <Navigate to={getRoleHome(role, isApproved)} replace />;
  }

  // Teachers can access their dashboard even if pending approval
  // Only block students/others who shouldn't be there
  if (role === "teacher" && isApproved === false && !effectiveAllowedRoles.includes("teacher")) {
    return <Navigate to="/teacher-dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;

// getTeacherHome function (fallback redirect mapping for manual navigation)
export const getTeacherHome = () => {
  return "/teacher-dashboard";
};
