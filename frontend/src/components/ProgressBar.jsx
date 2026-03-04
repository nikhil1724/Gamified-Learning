import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ current, total, showPercentage = true, size = 'medium' }) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className={`progress-bar-container ${size}`}>
      <div className="progress-bar-wrapper">
        <div className="progress-bar-track">
          <div 
            className="progress-bar-fill"
            style={{ width: `${percentage}%` }}
          >
            {showPercentage && percentage > 10 && (
              <span className="progress-percentage">{percentage}%</span>
            )}
          </div>
        </div>
        {showPercentage && percentage <= 10 && (
          <span className="progress-percentage-outside">{percentage}%</span>
        )}
      </div>
      <div className="progress-bar-stats">
        <span className="progress-current">{current}</span>
        <span className="progress-separator">/</span>
        <span className="progress-total">{total}</span>
        <span className="progress-label">completed</span>
      </div>
    </div>
  );
};

export default ProgressBar;
