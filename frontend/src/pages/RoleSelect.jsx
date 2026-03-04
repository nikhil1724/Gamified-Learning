import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

import AuthLayout from "../components/AuthLayout";
import "./RoleSelect.css";

const cardMotion = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: "easeOut" },
  },
};

const RoleSelect = () => {
  const navigate = useNavigate();

  const handleInstructorContinue = () => {
    navigate("/login/teacher");
  };

  return (
    <AuthLayout
      title="Choose Your Role"
      stacked
    >
      <div className="role-select-cards">
        <motion.div
          className="role-card"
          variants={cardMotion}
          initial="hidden"
          animate="show"
        >
          <div className="role-card__icon">🎓</div>
          <h3 className="role-card__title">Student</h3>
          <p className="role-card__description">Learn courses and participate in quizzes with adaptive recommendations.</p>
          <Link className="btn btn-primary btn-role" to="/login/student">
            Continue as Student
          </Link>
        </motion.div>

        <motion.div
          className="role-card"
          variants={cardMotion}
          initial="hidden"
          animate="show"
          transition={{ delay: 0.1 }}
        >
          <div className="role-card__icon">🧑‍🏫</div>
          <h3 className="role-card__title">Teacher</h3>
          <p className="role-card__description">Create courses, manage students, and track their progress.</p>
          <button
            type="button"
            className="btn btn-primary btn-role"
            onClick={handleInstructorContinue}
          >
            Continue as Teacher
          </button>
        </motion.div>

        <motion.div
          className="role-card"
          variants={cardMotion}
          initial="hidden"
          animate="show"
          transition={{ delay: 0.2 }}
        >
          <div className="role-card__icon">🛡️</div>
          <h3 className="role-card__title">Admin</h3>
          <p className="role-card__description">Manage approvals, users, and platform statistics.</p>
          <Link className="btn btn-primary btn-role" to="/login/admin">
            Continue as Admin
          </Link>
        </motion.div>
      </div>
    </AuthLayout>
  );
};

export default RoleSelect;
