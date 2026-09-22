import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Intercept fetch to automatically bypass ngrok free tier browser warning
const originalFetch = window.fetch;
window.fetch = async (input, init = {}) => {
  const url = typeof input === 'string' ? input : (input instanceof Request ? input.url : '');
  if (url.includes('ngrok')) {
    init = {
      ...init,
      headers: {
        ...(init.headers || {}),
        'ngrok-skip-browser-warning': 'true',
      },
    };
  }
  return originalFetch(input, init);
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
