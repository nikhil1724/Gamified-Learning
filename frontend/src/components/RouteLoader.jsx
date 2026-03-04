import "./RouteLoader.css";

const RouteLoader = ({ visible }) => (
  <div className={`route-loader ${visible ? "show" : "hide"}`}>
    <div className="route-loader__backdrop" />
    <div className="route-loader__card">
      <div className="route-loader__spinner" />
      <p className="mb-0 text-muted small">Loading</p>
    </div>
  </div>
);

export default RouteLoader;
