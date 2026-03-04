import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';
import './CodePlayground.css';

const CodePlayground = ({ language = 'python', initialCode = '' }) => {
  const [code, setCode] = useState(initialCode || getDefaultCode(language));
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const { theme } = useTheme();

  const handleRunCode = async () => {
    setIsRunning(true);
    setError(null);
    setOutput('Running code...');

    try {
      const response = await api.post('/api/run', {
        code: code,
        language: language
      });

      if (response.data.error) {
        setError(response.data.error);
        setOutput('');
      } else {
        setOutput(response.data.output || 'Code executed successfully!');
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to run code');
      setOutput('');
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    setCode(getDefaultCode(language));
    setOutput('');
    setError(null);
  };

  return (
    <div className="code-playground">
      <div className="playground-header">
        <div className="header-left">
          <i className="bi bi-code-square"></i>
          <span className="playground-title">Try it yourself</span>
          <span className="language-badge">{language}</span>
        </div>
        <div className="header-actions">
          <button className="btn-reset" onClick={handleReset} title="Reset code">
            <i className="bi bi-arrow-clockwise"></i>
            Reset
          </button>
          <button 
            className="btn-run" 
            onClick={handleRunCode} 
            disabled={isRunning}
          >
            {isRunning ? (
              <>
                <span className="spinner"></span>
                Running...
              </>
            ) : (
              <>
                <i className="bi bi-play-fill"></i>
                Run Code
              </>
            )}
          </button>
        </div>
      </div>

      <div className="editor-container">
        <Editor
          height="300px"
          language={language}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
          }}
        />
      </div>

      {(output || error) && (
        <div className="output-container">
          <div className="output-header">
            <i className={`bi bi-${error ? 'x-circle' : 'terminal'}`}></i>
            <span>{error ? 'Error' : 'Output'}</span>
          </div>
          <pre className={`output-content ${error ? 'error' : ''}`}>
            {error || output}
          </pre>
        </div>
      )}
    </div>
  );
};

function getDefaultCode(language) {
  const defaults = {
    python: `# Write your Python code here
print("Hello, World!")`,
    javascript: `// Write your JavaScript code here
console.log("Hello, World!");`,
    java: `// Write your Java code here
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}`,
    cpp: `// Write your C++ code here
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}`
  };
  return defaults[language] || '// Start coding...';
}

export default CodePlayground;
