import "./Footer.css";

const Footer = () => {
  return (
    <footer className="app-footer" aria-label="Site footer">
      <div className="app-footer__content">
        <p className="app-footer__text">Gamified Learning Platform &copy; 2026</p>
        <nav className="app-footer__links" aria-label="Footer links">
          <a href="/" className="app-footer__link">
            About
          </a>
          <a href="mailto:support@gamifiedlearningplatform.com" className="app-footer__link">
            Contact
          </a>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
