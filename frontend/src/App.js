import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { Suspense, lazy, useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import SplashScreen from "./components/SplashScreen";
import AchievementToastHost from "./components/AchievementToastHost";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Leaderboard from "./pages/Leaderboard";
import Login from "./pages/Login";
import Quiz from "./pages/Quiz";
import Register from "./pages/Register";
import Rewards from "./pages/Rewards";
import RoleSelect from "./pages/RoleSelect";
import SkillTree from "./pages/SkillTree";
import TeacherCourses from "./pages/TeacherCourses";
import StudentCourses from "./pages/StudentCourses";
import CourseContent from "./pages/CourseContent";
import CourseList from "./pages/CourseList";
import CourseDetail from "./pages/CourseDetail";
import LessonViewer from "./pages/LessonViewer";
import AdminTeachers from "./pages/AdminTeachers";
import AdminProblems from "./pages/AdminProblems";
import AdminCourseContent from "./pages/AdminCourseContent";
import ProblemsList from "./pages/ProblemsList";
import ProblemDetail from "./pages/ProblemDetail";
import RouteLoader from "./components/RouteLoader";
import LearnHub from "./pages/LearnHub";
import CourseLessons from "./pages/CourseLessons";
import LessonPage from "./pages/LessonPage";
import MyLearningDashboard from "./pages/MyLearningDashboard";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import TeacherStudents from "./pages/TeacherStudents";
import StudentPerformanceDetail from "./pages/StudentPerformanceDetail";
import CourseAnalytics from "./pages/CourseAnalytics";
import InstructorAnalytics from "./pages/InstructorAnalytics";
import VerifyEmail from "./pages/VerifyEmail";
import VerifyOTP from "./pages/VerifyOTP";
import VerifyEmailOTP from "./pages/VerifyEmailOTP";
import ResendVerification from "./pages/ResendVerification";
const StudentDashboard = lazy(() => import("./pages/StudentDashboard"));
const InstructorDashboard = lazy(() => import("./pages/InstructorDashboard"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));

const getRoleHome = (role, isApproved) => {
  if (role === "admin") {
    return "/admin/dashboard";
  }
  if (!role) {
    return "/role-select";
  }
  return role === "teacher" ? "/teacher/dashboard" : "/learn";
};

const AppRoutes = ({ isAuthenticated, role, isApproved }) => {
  const location = useLocation();
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    setShowLoader(true);
    const timer = setTimeout(() => setShowLoader(false), 400);
    return () => clearTimeout(timer);
  }, [location.pathname]);

  return (
    <>
      <RouteLoader visible={showLoader} />
      <AnimatePresence mode="wait">
        <Suspense fallback={<SplashScreen />}>
          <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to={getRoleHome(role, isApproved)} replace />
            ) : (
              <Home />
            )
          }
        />
        <Route
          path="/role-select"
          element={
            isAuthenticated && role ? (
              <Navigate to={getRoleHome(role, isApproved)} replace />
            ) : (
              <RoleSelect />
            )
          }
        />
        <Route path="/login" element={<Navigate to="/role-select" replace />} />
        <Route path="/login/student" element={<Login />} />
        <Route path="/login/teacher" element={<Login />} />
        <Route path="/login/admin" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/register/teacher" element={<Register />} />
        <Route path="/verify-email/:token" element={<VerifyEmail />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/verify-email-otp" element={<VerifyEmailOTP />} />
        <Route path="/resend-otp" element={<ResendVerification />} />
        <Route path="/resend-verification" element={<ResendVerification />} />
        <Route
          path="/home"
          element={<Navigate to={getRoleHome(role, isApproved)} replace />}
        />
        <Route
          path="/dashboard"
          element={<Navigate to={getRoleHome(role, isApproved)} replace />}
        />
        <Route
          path="/learn"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <LearnHub />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-learning"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <MyLearningDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/course/:course/lessons"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <CourseLessons />
            </ProtectedRoute>
          }
        />
        <Route
          path="/course/:course/:lesson"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <LessonPage />
            </ProtectedRoute>
          }
        />
          <Route
            path="/courses"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <CourseList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <CourseDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId/lessons/:lessonId"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <LessonViewer />
              </ProtectedRoute>
            }
          />
        <Route
          path="/learn/courses"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <StudentCourses />
            </ProtectedRoute>
          }
        />
        <Route
          path="/learn/courses/:courseId"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <CourseContent />
            </ProtectedRoute>
          }
        />
        <Route
          path="/problems"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <ProblemsList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/problems/:problemId"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <ProblemDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/teachers"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminTeachers />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/dashboard"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <InstructorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/courses"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <TeacherCourses />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/problems"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <AdminProblems />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/course-content"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <AdminCourseContent />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/students"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <TeacherStudents />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/student/:studentId"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <StudentPerformanceDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/course/:courseId/analytics"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <CourseAnalytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/instructor/analytics/:courseId"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <InstructorAnalytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/quiz"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Quiz />
            </ProtectedRoute>
          }
        />
        <Route
          path="/skills"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <SkillTree />
            </ProtectedRoute>
          }
        />
        <Route
          path="/rewards"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Rewards />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leaderboard"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Leaderboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute allowedRoles={["student", "teacher"]}>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute allowedRoles={["student", "teacher"]}>
              <Settings />
            </ProtectedRoute>
          }
        />
          </Routes>
        </Suspense>
      </AnimatePresence>
    </>
  );
};

const App = () => {
  const { isAuthenticated, authLoading, role, isApproved } = useAuth();

  if (authLoading) {
    return <SplashScreen />;
  }
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <Navbar />
      <AchievementToastHost />
      <AppRoutes
        isAuthenticated={isAuthenticated}
        role={role}
        isApproved={isApproved}
      />
    </BrowserRouter>
  );
};

export default App;
