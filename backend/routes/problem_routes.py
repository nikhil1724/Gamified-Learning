import os
import ast
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import db
from models import (
    CodeSubmission,
    Problem,
    ProblemProgress,
    ProblemTestCase,
    User,
    UserCodingStats,
)


problem_bp = Blueprint("problems", __name__, url_prefix="/api")

DIFFICULTY_XP = {
    "Easy": 10,
    "Medium": 20,
    "Hard": 30,
}

MAX_CODE_LENGTH = 20_000
DEFAULT_TIMEOUT_SECONDS = 2
MAX_TIMEOUT_SECONDS = 5
ALLOWED_LANGUAGE = "python"

BLOCKED_MODULES = {
    "os",
    "subprocess",
    "socket",
    "pathlib",
    "shutil",
    "ctypes",
    "multiprocessing",
    "threading",
    "requests",
    "urllib",
    "http",
    "importlib",
    "pickle",
    "marshal",
}

BLOCKED_CALLS = {
    "eval",
    "exec",
    "open",
    "compile",
    "__import__",
    "globals",
    "locals",
    "vars",
    "breakpoint",
}


def _validate_code(code):
    if not isinstance(code, str):
        return False, "Code must be a string."

    if not code.strip():
        return False, "Code cannot be empty."

    if len(code) > MAX_CODE_LENGTH:
        return False, f"Code is too long (max {MAX_CODE_LENGTH} characters)."

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Syntax Error: {exc.msg} (line {exc.lineno})"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                root_module = imported.name.split(".")[0]
                if root_module in BLOCKED_MODULES:
                    return False, f"Import '{root_module}' is not allowed."

        if isinstance(node, ast.ImportFrom):
            module_name = (node.module or "").split(".")[0]
            if module_name in BLOCKED_MODULES:
                return False, f"Import from '{module_name}' is not allowed."

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                return False, f"Use of '{node.func.id}' is not allowed."

            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in {"os", "subprocess", "socket", "pathlib", "shutil"}:
                        return False, f"Use of '{node.func.value.id}' is not allowed."

    return True, ""


def _safe_timeout(raw_timeout):
    try:
        timeout = int(raw_timeout)
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_SECONDS

    return max(1, min(timeout, MAX_TIMEOUT_SECONDS))


def _normalize_output(value):
    return (value or "").strip()


def _run_python_code(code, test_cases, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
    results = []
    total_runtime_ms = 0

    is_valid, validation_error = _validate_code(code)
    if not is_valid:
        return [
            {
                "passed": False,
                "error": validation_error,
                "runtime_ms": 0,
            }
        ], 0

    timeout_seconds = _safe_timeout(timeout_seconds)

    with tempfile.TemporaryDirectory(prefix="code_exec_") as run_dir:
        temp_path = os.path.join(run_dir, "solution.py")
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(code)

        for test_case in test_cases:
            start = time.perf_counter()
            try:
                process = subprocess.run(
                    [sys.executable, "-I", "-B", "-S", "-u", temp_path],
                    input=test_case.input_data,
                    text=True,
                    capture_output=True,
                    timeout=timeout_seconds,
                    cwd=run_dir,
                    env={
                        "PYTHONNOUSERSITE": "1",
                        "PYTHONDONTWRITEBYTECODE": "1",
                    },
                )
                runtime_ms = int((time.perf_counter() - start) * 1000)
                total_runtime_ms += runtime_ms

                if process.returncode != 0:
                    results.append(
                        {
                            "passed": False,
                            "error": process.stderr.strip() or "Runtime Error",
                            "runtime_ms": runtime_ms,
                        }
                    )
                    continue

                actual_output = _normalize_output(process.stdout)
                expected_output = _normalize_output(test_case.expected_output)
                passed = actual_output == expected_output
                results.append(
                    {
                        "passed": passed,
                        "actual_output": actual_output,
                        "expected_output": expected_output,
                        "runtime_ms": runtime_ms,
                    }
                )
            except subprocess.TimeoutExpired:
                results.append(
                    {
                        "passed": False,
                        "error": "Time Limit Exceeded",
                        "runtime_ms": int((time.perf_counter() - start) * 1000),
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "passed": False,
                        "error": f"Runtime Error: {exc}",
                        "runtime_ms": int((time.perf_counter() - start) * 1000),
                    }
                )

    return results, total_runtime_ms


def _get_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id)) if user_id is not None else None


def _update_coding_stats(user, solved, solved_at):
    stats = UserCodingStats.query.filter_by(user_id=user.id).first()
    if not stats:
        stats = UserCodingStats(user_id=user.id)
        db.session.add(stats)

    if solved:
        if stats.last_solved_at:
            last_date = stats.last_solved_at.date()
            current_date = solved_at.date()
            if current_date == last_date:
                pass
            elif current_date == last_date + timedelta(days=1):
                stats.streak_days += 1
            else:
                stats.streak_days = 1
        else:
            stats.streak_days = 1

        stats.solved_count += 1
        stats.last_solved_at = solved_at

    return stats


def _upsert_progress(user_id, problem_id, solved, runtime_ms, submission_id):
    progress = ProblemProgress.query.filter_by(
        user_id=user_id, problem_id=problem_id
    ).first()
    if not progress:
        progress = ProblemProgress(user_id=user_id, problem_id=problem_id)
        db.session.add(progress)

    if solved:
        progress.solved = True
        if runtime_ms is not None:
            if progress.best_runtime_ms is None or runtime_ms < progress.best_runtime_ms:
                progress.best_runtime_ms = runtime_ms

    progress.last_submission_id = submission_id
    progress.updated_at = datetime.utcnow()
    return progress


@problem_bp.get("/problems")
def list_problems():
    problems = Problem.query.order_by(Problem.created_at.desc()).all()
    data = [
        {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "tags": problem.tags or [],
        }
        for problem in problems
    ]
    return jsonify({"success": True, "data": data})


@problem_bp.get("/problem/<int:problem_id>")
def get_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    public_tests = [
        {
            "id": test.id,
            "input": test.input_data,
            "expected_output": test.expected_output,
        }
        for test in problem.test_cases
        if not test.is_hidden
    ]

    data = {
        "id": problem.id,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "tags": problem.tags or [],
        "description": problem.description,
        "constraints": problem.constraints,
        "example_input": problem.example_input,
        "example_output": problem.example_output,
        "test_cases": public_tests,
    }
    return jsonify({"success": True, "data": data})


@problem_bp.post("/run")
@jwt_required()
def run_code():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code")
    problem_id = payload.get("problem_id")
    timeout_seconds = payload.get("timeout_seconds")

    if not code or not problem_id:
        return jsonify({"success": False, "error": "Missing code or problem_id"}), 400

    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    test_cases = [test for test in problem.test_cases if not test.is_hidden]
    results, runtime_ms = _run_python_code(code, test_cases, timeout_seconds=timeout_seconds)

    passed_count = sum(1 for result in results if result.get("passed"))
    data = {
        "results": results,
        "passed_count": passed_count,
        "total_count": len(test_cases),
        "runtime_ms": runtime_ms,
    }
    return jsonify({"success": True, "data": data})


@problem_bp.post("/submit")
@jwt_required()
def submit_code():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code")
    problem_id = payload.get("problem_id")
    language = (payload.get("language") or ALLOWED_LANGUAGE).lower()
    timeout_seconds = payload.get("timeout_seconds")

    if not code or not problem_id:
        return jsonify({"success": False, "error": "Missing code or problem_id"}), 400
    if language != ALLOWED_LANGUAGE:
        return jsonify({"success": False, "error": "Only Python is supported"}), 400

    user = _get_user()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    test_cases = list(problem.test_cases)
    results, runtime_ms = _run_python_code(code, test_cases, timeout_seconds=timeout_seconds)
    passed_count = sum(1 for result in results if result.get("passed"))
    total_count = len(test_cases)
    all_passed = passed_count == total_count

    if all_passed:
        status = "Accepted"
    else:
        status = "Wrong Answer"
        if any(result.get("error") == "Time Limit Exceeded" for result in results):
            status = "Time Limit Exceeded"
        elif any((result.get("error") or "").startswith("Runtime Error") for result in results):
            status = "Runtime Error"

    submission = CodeSubmission(
        user_id=user.id,
        problem_id=problem.id,
        language=ALLOWED_LANGUAGE,
        code=code,
        status=status,
        runtime_ms=runtime_ms,
        passed_count=passed_count,
        total_count=total_count,
    )
    db.session.add(submission)
    db.session.flush()

    _upsert_progress(user.id, problem.id, all_passed, runtime_ms, submission.id)

    if all_passed:
        user.xp_points += DIFFICULTY_XP.get(problem.difficulty, 10)
        _update_coding_stats(user, solved=True, solved_at=datetime.utcnow())

    db.session.commit()

    data = {
        "submission_id": submission.id,
        "status": submission.status,
        "runtime_ms": submission.runtime_ms,
        "passed_count": submission.passed_count,
        "total_count": submission.total_count,
    }
    return jsonify({"success": True, "data": data})


@problem_bp.get("/submissions/<int:user_id>")
@jwt_required()
def list_submissions(user_id):
    user = _get_user()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if user.id != user_id and user.role != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    submissions = (
        CodeSubmission.query.filter_by(user_id=user_id)
        .order_by(CodeSubmission.created_at.desc())
        .limit(50)
        .all()
    )
    data = [
        {
            "id": submission.id,
            "problem_id": submission.problem_id,
            "status": submission.status,
            "runtime_ms": submission.runtime_ms,
            "passed_count": submission.passed_count,
            "total_count": submission.total_count,
            "created_at": submission.created_at.isoformat(),
        }
        for submission in submissions
    ]
    return jsonify({"success": True, "data": data})
