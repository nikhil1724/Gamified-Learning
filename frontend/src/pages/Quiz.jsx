import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import Confetti from "react-confetti";
import PageTransition from "../components/PageTransition";
import { SkeletonCard } from "../components/Skeletons";
import "./Quiz.css";

const Quiz = () => {
  const [searchParams] = useSearchParams();
  const autoSelectedRef = useRef(false);
  const { isAuthenticated, token } = useAuth();
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [unlockedBadges, setUnlockedBadges] = useState([]);
  const [showAchievement, setShowAchievement] = useState(false);
  const [achievementBadges, setAchievementBadges] = useState([]);
  const [quizHistory, setQuizHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [timeUpSubmitted, setTimeUpSubmitted] = useState(false);
  const [showXpGain, setShowXpGain] = useState(false);
  const [confettiSize, setConfettiSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        setLoading(true);
        const response = await api.get("/quizzes");
        setQuizzes(response.data || []);
      } catch (err) {
        setError(err?.response?.data?.error || "Failed to load quizzes.");
      } finally {
        setLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!isAuthenticated) {
        setQuizHistory([]);
        return;
      }

      try {
        setHistoryLoading(true);
        const response = await api.get("/quiz/history");
        setQuizHistory(Array.isArray(response.data) ? response.data : []);
      } catch {
        setQuizHistory([]);
      } finally {
        setHistoryLoading(false);
      }
    };

    fetchHistory();
  }, [isAuthenticated]);

  const currentQuestion = useMemo(
    () => questions[currentIndex],
    [questions, currentIndex]
  );

  const handleSelectQuiz = useCallback(async (quiz) => {
    setSelectedQuiz(quiz);
    setResult(null);
    setAnswers({});
    setCurrentIndex(0);
    setError("");

    try {
      setLoading(true);
      const response = await api.get(`/quiz/${quiz.id}`);
      const loadedQuestions = response.data?.questions || [];
      setQuestions(loadedQuestions);
    } catch (err) {
      const errMsg = err?.response?.data?.error || "Failed to load quiz.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (autoSelectedRef.current || quizzes.length === 0) {
      return;
    }

    const quizId = searchParams.get("quizId");
    if (!quizId) {
      return;
    }

    const match = quizzes.find((quiz) => String(quiz.id) === quizId);
    if (match) {
      autoSelectedRef.current = true;
      handleSelectQuiz(match);
    }
  }, [quizzes, searchParams, handleSelectQuiz]);

  const handleNext = () => {
    if (!currentQuestion) {
      return;
    }

    const selected = answers[currentQuestion.id];
    if (!selected) {
      return;
    }

    setCurrentIndex((prev) => {
      if (prev >= questions.length - 1) {
        return prev;
      }
      return prev + 1;
    });
  };

  const handleAnswerChange = (questionId, optionKey) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey,
    }));
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!selectedQuiz) {
      return;
    }

    if (!isAuthenticated) {
      setError("Please log in to submit your quiz.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const response = await api.post(
        "/quiz/submit",
        {
          quiz_id: selectedQuiz.id,
          answers,
        },
        token
          ? {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          : undefined
      );
      setResult(response.data);
      setShowXpGain(true);
      window.setTimeout(() => setShowXpGain(false), 2200);
      const unlocked = response.data?.unlocked_badges || [];
      setUnlockedBadges(unlocked);
      if (Array.isArray(unlocked) && unlocked.length) {
        window.dispatchEvent(
          new CustomEvent("achievement:unlock", { detail: { badges: unlocked } })
        );
      }
      try {
        const storedResult = {
          score: response.data?.score ?? 0,
          total_questions: response.data?.total_questions ?? questions.length,
          completed_at: new Date().toISOString(),
        };
        localStorage.setItem(
          `quiz_result_${selectedQuiz.id}`,
          JSON.stringify(storedResult)
        );
      } catch {
        // Ignore storage errors (e.g., quota).
      }

      try {
        const historyResponse = await api.get("/quiz/history");
        setQuizHistory(Array.isArray(historyResponse.data) ? historyResponse.data : []);
      } catch {
        // Ignore history refresh errors.
      }
    } catch (err) {
      const message =
        err?.response?.data?.error ||
        err?.response?.data?.msg ||
        "Failed to submit quiz.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedQuiz(null);
    setQuestions([]);
    setAnswers({});
    setCurrentIndex(0);
    setResult(null);
    setUnlockedBadges([]);
    setAchievementBadges([]);
    setShowAchievement(false);
    setTimeLeft(0);
    setTimeUpSubmitted(false);
    setError("");
  };

  useEffect(() => {
    if (!selectedQuiz || result || questions.length === 0) {
      return;
    }

    setTimeLeft(questions.length * 30);
    setTimeUpSubmitted(false);
  }, [selectedQuiz, result, questions.length]);

  useEffect(() => {
    if (!selectedQuiz || result || questions.length === 0 || timeLeft <= 0) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      setTimeLeft((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [selectedQuiz, result, questions.length, timeLeft]);

  useEffect(() => {
    if (
      selectedQuiz &&
      !result &&
      questions.length > 0 &&
      timeLeft === 0 &&
      !timeUpSubmitted
    ) {
      setTimeUpSubmitted(true);
      handleSubmit();
    }
  }, [selectedQuiz, result, questions.length, timeLeft, timeUpSubmitted]);

  const timerLabel = useMemo(() => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    return `${minutes}:${String(seconds).padStart(2, "0")}`;
  }, [timeLeft]);

  useEffect(() => {
    if (unlockedBadges.length === 0) {
      return;
    }

    setAchievementBadges(unlockedBadges);
    setShowAchievement(true);

    const closeTimer = setTimeout(() => {
      setShowAchievement(false);
    }, 3800);

    return () => clearTimeout(closeTimer);
  }, [unlockedBadges]);

  useEffect(() => {
    if (!showAchievement) {
      return;
    }

    const playAchievementSound = () => {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.type = "triangle";
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.18, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(
          0.001,
          audioContext.currentTime + 0.7
        );

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.7);

        setTimeout(() => audioContext.close(), 900);
      } catch (soundError) {
        // Ignore audio errors (e.g., autoplay restrictions).
      }
    };

    playAchievementSound();
  }, [showAchievement]);

  useEffect(() => {
    const handleResize = () => {
      setConfettiSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const fallbackBadgeSvg = encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient></defs><circle cx="48" cy="48" r="40" fill="url(#g)"/><circle cx="48" cy="48" r="30" fill="#fff" opacity="0.2"/><path d="M48 26l6.5 13.2L69 41.3l-10.5 10.2L61 66l-13-6.9L35 66l2.5-14.5L27 41.3l14.5-2.1L48 26z" fill="#fff"/></svg>'
  );
  const fallbackBadgeImage = `data:image/svg+xml;utf8,${fallbackBadgeSvg}`;

  return (
    <PageTransition>
      <div className="container py-5 quiz-page">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2 quiz-page__header">
        <div>
          <h1 className="mb-2">Quiz</h1>
          <p className="text-muted mb-0">Answer questions and boost your score.</p>
        </div>
        {selectedQuiz ? (
          <button className="btn btn-outline-secondary" onClick={handleReset}>
            Back to quizzes
          </button>
        ) : null}
      </div>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      {!selectedQuiz ? (
        <div className="row g-4 quiz-page__grid">
          {loading ? (
            Array.from({ length: 6 }).map((_, index) => (
              <div className="col-12 col-md-6 col-lg-4" key={`quiz-skeleton-${index}`}>
                <SkeletonCard />
              </div>
            ))
          ) : quizzes.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-info">No quizzes available yet.</div>
            </div>
          ) : (
            quizzes.map((quiz) => (
              <div className="col-12 col-md-6 col-lg-4" key={quiz.id}>
                <div className="card h-100 shadow-sm quiz-select-card">
                  <div className="card-body d-flex flex-column">
                    <h5 className="card-title">{quiz.title}</h5>
                    <p className="card-text text-muted mb-2">{quiz.topic}</p>
                    <div className="d-flex flex-wrap gap-2 mb-3">
                      <span className="badge bg-primary align-self-start">
                        {quiz.difficulty}
                      </span>
                      <span className="badge bg-light text-dark border">
                        ⚡ {quiz.xp_reward || 0} XP
                      </span>
                      <span className="badge bg-light text-dark border">
                        {quiz.question_count || 0} Qs
                      </span>
                    </div>
                    <button
                      className="btn btn-outline-primary mt-auto"
                      onClick={() => handleSelectQuiz(quiz)}
                    >
                      Start Quiz
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      ) : null}

      {selectedQuiz && !loading && result ? (
        <div className="card shadow-sm quiz-result-card">
          <div className="card-body">
            {showXpGain ? (
              <div className="xp-gain-pop">+{result.xp_earned || 0} XP</div>
            ) : null}
            <h4 className="mb-3">Quiz Completed</h4>
            <p className="mb-2">
              <strong>Score:</strong> {result.score} / {result.total_questions}
            </p>
            <p className="mb-2">
              <strong>Accuracy:</strong> {result.percentage}%
            </p>
            <p className="mb-2">
              <strong>XP Earned:</strong> {result.xp_earned}
            </p>
            <p className="mb-0">
              <strong>Coins Earned:</strong> {result.coins_earned}
            </p>

            <div className="mt-3 d-flex flex-wrap gap-2">
              <button type="button" className="btn btn-primary" onClick={() => {
                setResult(null);
                setAnswers({});
                setCurrentIndex(0);
                setTimeUpSubmitted(false);
                setTimeLeft(questions.length * 30);
              }}>
                Retry Quiz
              </button>
              <button type="button" className="btn btn-outline-secondary" onClick={handleReset}>
                Back to Quiz List
              </button>
            </div>

            {Array.isArray(result.question_results) && result.question_results.length > 0 ? (
              <div className="quiz-review mt-4">
                <h5 className="mb-3">Answer Review</h5>
                <div className="quiz-review-list">
                  {result.question_results.map((entry, idx) => (
                    <div
                      key={entry.question_id}
                      className={`quiz-review-item ${entry.is_correct ? "is-correct" : "is-incorrect"}`}
                    >
                      <div className="quiz-review-item__title">
                        Q{idx + 1}. {entry.question_text}
                      </div>
                      <div className="quiz-review-item__meta">
                        <span>Your answer: {entry.selected_option || "Not answered"}</span>
                        <span>Correct: {entry.correct_option}</span>
                      </div>
                      {entry.explanation ? (
                        <p className="quiz-review-item__explanation mb-0">{entry.explanation}</p>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      ) : null}

      {!selectedQuiz ? (
        <div className="card shadow-sm quiz-history-card mt-4">
          <div className="card-body">
            <h5 className="mb-3">Quiz History</h5>
            {historyLoading ? (
              <div className="text-muted">Loading history...</div>
            ) : quizHistory.length === 0 ? (
              <div className="text-muted">No attempts yet.</div>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm align-middle mb-0">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Score</th>
                      <th>Accuracy</th>
                      <th>Attempted</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quizHistory.slice(0, 10).map((attempt) => (
                      <tr key={attempt.attempt_id}>
                        <td>{attempt.quiz_title}</td>
                        <td>{attempt.score}/{attempt.total_questions}</td>
                        <td>{attempt.percentage}%</td>
                        <td>{new Date(attempt.attempted_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : null}

      {showAchievement ? (
        <div className="achievement-modal">
          <Confetti
            width={confettiSize.width}
            height={confettiSize.height}
            numberOfPieces={220}
            recycle={false}
            gravity={0.25}
          />
          <div className="achievement-modal__overlay" />
          <div className="achievement-modal__card">
            <div className="achievement-modal__header">
              <span className="achievement-modal__chip">Achievement</span>
              <button
                type="button"
                className="btn btn-sm btn-light"
                onClick={() => setShowAchievement(false)}
              >
                Close
              </button>
            </div>
            <h4 className="mb-2">Badge Unlocked!</h4>
            <p className="text-muted mb-4">
              Great job! You just earned a new achievement.
            </p>
            <div className="achievement-modal__badges">
              {achievementBadges.map((badge) => (
                <div key={badge.id} className="achievement-modal__badge">
                  <img
                    src={badge.image_url || fallbackBadgeImage}
                    alt={badge.name}
                  />
                  <div>
                    <h6 className="mb-1">{badge.name}</h6>
                    <p className="mb-0 text-muted small">
                      {badge.description || "Achievement unlocked."}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}

      {selectedQuiz && !loading && !result ? (
        <div className="card shadow-sm quiz-session-card">
          <div className="card-body">
            <div className="d-flex flex-wrap justify-content-between align-items-center mb-3">
              <div>
                <h4 className="mb-1">{selectedQuiz.title}</h4>
                <p className="text-muted mb-0">{selectedQuiz.topic}</p>
              </div>
              <div className="d-flex gap-2 align-items-center">
                <span className="badge bg-dark">⏱ {timerLabel}</span>
                <span className="badge bg-primary">{selectedQuiz.difficulty}</span>
              </div>
            </div>

            <div className="progress mb-3" role="progressbar" aria-label="Question progress">
              <div
                className="progress-bar"
                style={{ width: `${Math.round(((currentIndex + 1) / Math.max(questions.length, 1)) * 100)}%` }}
              >
                Q{Math.min(currentIndex + 1, questions.length)}/{questions.length || 1}
              </div>
            </div>

            {currentQuestion ? (
              <>
                {!isAuthenticated ? (
                  <div className="alert alert-warning">
                    Please log in to submit your quiz results.
                  </div>
                ) : null}
                <div className="mb-4">
                  <p className="mb-2 text-muted">
                    Question {currentIndex + 1} of {questions.length}
                  </p>
                  <h5>{currentQuestion.question_text}</h5>
                </div>

                <div className="list-group mb-4">
                  {[
                    { key: "A", label: currentQuestion.option_a },
                    { key: "B", label: currentQuestion.option_b },
                    { key: "C", label: currentQuestion.option_c },
                    { key: "D", label: currentQuestion.option_d },
                  ].map((option) => (
                    <label
                      key={option.key}
                      htmlFor={`question-${currentQuestion.id}-${option.key}`}
                      className={`list-group-item d-flex gap-2 align-items-center ${
                        answers[currentQuestion.id] === option.key ? "active" : ""
                      }`}
                    >
                      <input
                        id={`question-${currentQuestion.id}-${option.key}`}
                        type="radio"
                        className="form-check-input"
                        name={`question-${currentQuestion.id}`}
                        value={option.key}
                        checked={answers[currentQuestion.id] === option.key}
                        onChange={() =>
                          handleAnswerChange(currentQuestion.id, option.key)
                        }
                      />
                      <span>{option.label}</span>
                    </label>
                  ))}
                </div>

                <div className="d-flex flex-wrap gap-2 justify-content-between">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={handlePrevious}
                    disabled={currentIndex === 0}
                  >
                    Previous
                  </button>
                  {currentIndex < questions.length - 1 ? (
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={handleNext}
                      disabled={!currentQuestion || !answers[currentQuestion.id]}
                    >
                      Next Question
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="btn btn-success"
                      onClick={handleSubmit}
                      disabled={Object.keys(answers).length === 0}
                    >
                      Submit Quiz
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="alert alert-info mb-0">
                No questions available for this quiz.
              </div>
            )}
          </div>
        </div>
      ) : null}
      </div>
    </PageTransition>
  );
};

export default Quiz;
