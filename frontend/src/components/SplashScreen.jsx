import "./SplashScreen.css";

const SplashScreen = () => {
  return (
    <div className="splash-screen">
      <div className="splash-card">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <h4 className="mt-3 mb-1">Gamified Learning</h4>
        <p className="text-muted mb-0">Preparing your dashboard...</p>
      </div>
    </div>
  );
};

export default SplashScreen;
