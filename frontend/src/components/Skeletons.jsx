import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import "./Skeletons.css";

export const SkeletonCard = () => (
  <div className="skeleton-card">
    <Skeleton height={18} width="65%" className="mb-2" />
    <Skeleton height={12} width="90%" className="mb-2" />
    <Skeleton height={12} width="80%" className="mb-3" />
    <Skeleton height={36} borderRadius={10} />
  </div>
);

export const SkeletonTable = ({ rows = 6, cols = 5 }) => (
  <div className="skeleton-table">
    <div className="skeleton-table__header">
      {Array.from({ length: cols }).map((_, idx) => (
        <Skeleton key={`head-${idx}`} height={16} />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, rowIdx) => (
      <div className="skeleton-table__row" key={`row-${rowIdx}`}>
        {Array.from({ length: cols }).map((_, colIdx) => (
          <Skeleton key={`cell-${rowIdx}-${colIdx}`} height={14} />
        ))}
      </div>
    ))}
  </div>
);

export const SkeletonStats = ({ items = 4 }) => (
  <div className="skeleton-stats">
    {Array.from({ length: items }).map((_, idx) => (
      <div className="skeleton-stat" key={`stat-${idx}`}>
        <Skeleton height={10} width="60%" className="mb-2" />
        <Skeleton height={24} width="40%" />
      </div>
    ))}
  </div>
);
