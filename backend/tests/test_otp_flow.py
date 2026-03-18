import os
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def _install_reportlab_stubs_if_missing():
    try:
        __import__("reportlab")
        return
    except Exception:
        pass

    reportlab = types.ModuleType("reportlab")
    lib = types.ModuleType("reportlab.lib")
    colors = types.ModuleType("reportlab.lib.colors")
    pagesizes = types.ModuleType("reportlab.lib.pagesizes")
    units = types.ModuleType("reportlab.lib.units")
    pdfgen = types.ModuleType("reportlab.pdfgen")
    canvas = types.ModuleType("reportlab.pdfgen.canvas")

    colors.HexColor = lambda *_args, **_kwargs: None
    colors.white = None
    pagesizes.A4 = (595, 842)
    units.inch = 72

    class _StubCanvas:
        def __init__(self, *_args, **_kwargs):
            pass

        def __getattr__(self, _name):
            def _noop(*_args, **_kwargs):
                return None

            return _noop

    canvas.Canvas = _StubCanvas

    sys.modules["reportlab"] = reportlab
    sys.modules["reportlab.lib"] = lib
    sys.modules["reportlab.lib.colors"] = colors
    sys.modules["reportlab.lib.pagesizes"] = pagesizes
    sys.modules["reportlab.lib.units"] = units
    sys.modules["reportlab.pdfgen"] = pdfgen
    sys.modules["reportlab.pdfgen.canvas"] = canvas


def _configure_test_env(temp_db_path: str):
    sqlite_path = Path(temp_db_path).resolve().as_posix()
    os.environ["DATABASE_URL"] = f"sqlite:///{sqlite_path}"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_DEBUG"] = "0"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-with-at-least-32-bytes"
    os.environ["EMAIL_VERIFICATION_REQUIRED"] = "true"
    os.environ["OTP_EXPIRY_MINUTES"] = "5"
    os.environ["OTP_RESEND_MAX_ATTEMPTS"] = "3"
    os.environ["OTP_RESEND_WINDOW_MINUTES"] = "15"
    os.environ["OTP_RESEND_COOLDOWN_SECONDS"] = "0"
    os.environ["OTP_VERIFY_MAX_ATTEMPTS"] = "3"
    os.environ["OTP_VERIFY_LOCK_MINUTES"] = "2"
    os.environ["MAIL_SERVER"] = "smtp.gmail.com"
    os.environ["MAIL_PORT"] = "587"
    os.environ["MAIL_USE_TLS"] = "true"
    os.environ["MAIL_USERNAME"] = "smtp-test@example.com"
    os.environ["MAIL_PASSWORD"] = "smtp-test-password"
    os.environ["AUTO_VERIFY_LEGACY_USERS"] = "false"
    os.environ["LEGACY_VERIFICATION_CUTOFF"] = ""
    os.environ["RUN_STARTUP_TASKS"] = "false"


class OtpFlowIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp_dir = tempfile.TemporaryDirectory(prefix="otp_flow_test_")
        cls._db_path = os.path.join(cls._tmp_dir.name, "otp_flow.sqlite3")
        _configure_test_env(cls._db_path)
        _install_reportlab_stubs_if_missing()

        import config

        config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        config.Config.SQLALCHEMY_ENGINE_OPTIONS = {}

        from app import create_app

        cls.app = create_app()
        cls.app.config.update(TESTING=True)

        from database import db

        cls.db = db
        with cls.app.app_context():
            cls.db.drop_all()
            cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            cls.db.session.remove()
            cls.db.drop_all()
            cls.db.engine.dispose()
        cls._tmp_dir.cleanup()

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            from models import User

            self.db.session.query(User).delete()
            self.db.session.commit()

    def _register_user(self, email="otp.user@example.com", password="Pass@1234"):
        payload = {
            "name": "OTP User",
            "email": email,
            "password": password,
            "role": "student",
        }

        with patch("routes.auth_routes.send_otp_email", return_value=True):
            response = self.client.post("/api/register", json=payload)

        return response

    def _get_user(self, email):
        from models import User

        return self.db.session.query(User).filter_by(email=email).first()

    def test_register_blocks_login_until_otp_verified_then_allows_login(self):
        email = "otp.flow@example.com"
        password = "Pass@1234"

        register_response = self._register_user(email=email, password=password)
        self.assertEqual(register_response.status_code, 201)
        register_data = register_response.get_json()
        self.assertEqual(register_data.get("email_sent"), True)
        self.assertNotIn("verification_otp", register_data)

        login_before_verify = self.client.post(
            "/api/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(login_before_verify.status_code, 401)

        with self.app.app_context():
            user = self._get_user(email)
            self.assertIsNotNone(user)
            self.assertFalse(user.is_verified)
            self.assertIsNotNone(user.otp_code)
            self.assertEqual(len(user.otp_code), 64)
            raw_otp = user.verification_token
            self.assertIsNotNone(raw_otp)
            self.assertEqual(len(raw_otp), 6)

        verify_response = self.client.post(
            "/api/verify-otp",
            json={"email": email, "otp": raw_otp},
        )
        self.assertEqual(verify_response.status_code, 200)

        with self.app.app_context():
            user = self._get_user(email)
            self.assertTrue(user.is_verified)
            self.assertTrue(user.email_verified)
            self.assertIsNone(user.otp_code)
            self.assertIsNone(user.otp_expiry)

        login_after_verify = self.client.post(
            "/api/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(login_after_verify.status_code, 200)
        self.assertIn("token", login_after_verify.get_json())

    def test_verify_with_invalid_otp_is_rejected(self):
        email = "otp.invalid@example.com"
        self._register_user(email=email)

        verify_response = self.client.post(
            "/api/verify-otp",
            json={"email": email, "otp": "000000"},
        )
        self.assertEqual(verify_response.status_code, 400)

    def test_resend_otp_rate_limit(self):
        email = "otp.resend@example.com"
        self._register_user(email=email)

        with self.app.app_context():
            user = self._get_user(email)
            user.otp_last_sent_at = None
            self.db.session.commit()

        with patch("routes.auth_routes.send_otp_email", return_value=True):
            first = self.client.post("/api/resend-otp", json={"email": email})
            second = self.client.post("/api/resend-otp", json={"email": email})
            third = self.client.post("/api/resend-otp", json={"email": email})
            fourth = self.client.post("/api/resend-otp", json={"email": email})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 200)
        self.assertEqual(fourth.status_code, 429)

    def test_verify_otp_lockout_after_invalid_attempts(self):
        email = "otp.lock@example.com"
        self._register_user(email=email)

        first = self.client.post("/api/verify-otp", json={"email": email, "otp": "000000"})
        second = self.client.post("/api/verify-otp", json={"email": email, "otp": "000000"})
        third = self.client.post("/api/verify-otp", json={"email": email, "otp": "000000"})

        self.assertEqual(first.status_code, 400)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(third.status_code, 429)

        payload = third.get_json()
        self.assertIn("retry_after_seconds", payload)

    def test_resend_otp_cooldown_enforced(self):
        email = "otp.cooldown@example.com"
        self._register_user(email=email)

        with self.app.app_context():
            self.app.config["OTP_RESEND_COOLDOWN_SECONDS"] = 120
            user = self._get_user(email)
            user.otp_last_sent_at = datetime.utcnow()
            self.db.session.commit()

        response = self.client.post("/api/resend-otp", json={"email": email})
        self.assertEqual(response.status_code, 429)

        payload = response.get_json()
        self.assertEqual(payload.get("error"), "Resend cooldown active")
        self.assertGreater(payload.get("retry_after_seconds", 0), 0)

        with self.app.app_context():
            self.app.config["OTP_RESEND_COOLDOWN_SECONDS"] = 0
            user = self._get_user(email)
            user.otp_last_sent_at = datetime.utcnow() - timedelta(minutes=3)
            self.db.session.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
