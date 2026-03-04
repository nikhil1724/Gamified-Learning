import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './MarkdownLessonViewer.css';

const MarkdownLessonViewer = ({ course, lesson }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMarkdown = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch markdown from public folder
        const response = await fetch(`/content/${course}/lesson${lesson}.md`);
        if (!response.ok) {
          throw new Error('Lesson not found');
        }
        const text = await response.text();
        
        setContent(text);
        setLoading(false);
      } catch (err) {
        console.error('Error loading markdown:', err);
        setError('Lesson not found. Please check the course and lesson number.');
        setLoading(false);
      }
    };

    if (course && lesson) {
      loadMarkdown();
    }
  }, [course, lesson]);

  if (loading) {
    return (
      <div className="markdown-viewer">
        <div className="loading-skeleton">
          <div className="skeleton-title"></div>
          <div className="skeleton-text"></div>
          <div className="skeleton-text"></div>
          <div className="skeleton-code"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="markdown-viewer">
        <div className="error-message">
          <i className="bi bi-exclamation-triangle"></i>
          <h3>Oops!</h3>
          <p>{error}</p>
          <div className="error-details">
            <p>Course: <strong>{course}</strong></p>
            <p>Lesson: <strong>{lesson}</strong></p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="markdown-viewer">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom code block rendering with syntax highlighting
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            return !inline && language ? (
              <SyntaxHighlighter
                style={oneDark}
                language={language}
                PreTag="div"
                className="code-block"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          // Custom heading rendering with anchor links
          h1: ({ children }) => (
            <h1 className="markdown-h1">
              {children}
              <span className="heading-decoration"></span>
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="markdown-h2">
              {children}
              <span className="heading-decoration"></span>
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="markdown-h3">{children}</h3>
          ),
          // Custom list rendering
          ul: ({ children }) => (
            <ul className="markdown-list">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="markdown-ordered-list">{children}</ol>
          ),
          // Custom blockquote
          blockquote: ({ children }) => (
            <blockquote className="markdown-blockquote">{children}</blockquote>
          ),
          // Custom table
          table: ({ children }) => (
            <div className="table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          // Custom link
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="markdown-link">
              {children}
              <i className="bi bi-box-arrow-up-right ms-1"></i>
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownLessonViewer;
