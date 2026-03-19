from flask_socketio import SocketIO, emit


socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")


def init_socketio(app):
    socketio.init_app(
        app,
        async_mode="threading",
        cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"),
        ping_interval=25,
        ping_timeout=60,
        allow_upgrades=False,
    )


@socketio.on("connect")
def on_connect():
    from leaderboard_service import build_full_leaderboard_payload

    emit("leaderboard:update", build_full_leaderboard_payload())


@socketio.on("leaderboard:subscribe")
def on_leaderboard_subscribe():
    from leaderboard_service import build_full_leaderboard_payload

    emit("leaderboard:update", build_full_leaderboard_payload())
