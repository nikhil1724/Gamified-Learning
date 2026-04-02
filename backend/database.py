import logging
import time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


db = SQLAlchemy()


def init_db(app):
	"""Bind SQLAlchemy to the Flask app instance."""
	db.init_app(app)


def register_db_observability(app) -> None:
	"""Attach lightweight SQLAlchemy event logging for production diagnostics."""
	logger = logging.getLogger(__name__)

	with app.app_context():
		engine = db.engine

	@event.listens_for(engine, "handle_error")
	def _on_handle_error(ctx):
		# `is_disconnect` identifies transport-level failures that often recover on retry.
		logger.warning(
			"SQLAlchemy runtime DB error disconnect=%s statement=%s",
			bool(getattr(ctx, "is_disconnect", False)),
			(getattr(ctx, "statement", None) or "").splitlines()[0][:160],
		)

	@event.listens_for(engine.pool, "invalidate")
	def _on_invalidate(dbapi_connection, connection_record, exception):
		logger.warning("SQLAlchemy invalidated a DB connection: %s", exception)


def check_database_connection(app, attempts: int = 3, delay_seconds: float = 2.0) -> bool:
	"""Run a non-fatal startup connectivity check with retries."""
	logger = logging.getLogger(__name__)

	with app.app_context():
		for attempt in range(1, attempts + 1):
			try:
				with db.engine.connect() as conn:
					conn.execute(text("SELECT 1"))
				logger.info("Database connectivity check succeeded on attempt %s/%s", attempt, attempts)
				return True
			except SQLAlchemyError as exc:
				logger.warning(
					"Database connectivity check failed on attempt %s/%s: %s",
					attempt,
					attempts,
					exc,
				)
				db.session.remove()
				db.engine.dispose()
				if attempt < attempts:
					time.sleep(delay_seconds)

	logger.warning("Continuing startup without confirmed database connectivity")
	return False
