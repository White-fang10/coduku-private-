/**
 * pistonService.js
 * Routes code execution through the Judge Service (Judge0-backed).
 * Falls back to the Flask backend's local executor if Judge Service is unavailable.
 */

const JUDGE_API  = process.env.REACT_APP_JUDGE_URL  || 'http://localhost:8002';
const BACKEND_API = localStorage.getItem('NGROK_URL') || process.env.REACT_APP_API_URL   || 'https://coduku-backend.onrender.com';

/**
 * Run code via the Judge Service (Judge0).
 * Uses problem_id=1 as a scratch pad with custom stdin.
 */
export async function runCode(language, code, stdin = '', token = '') {
  // First try the Judge Service
  try {
    const res = await fetch(`${JUDGE_API}/api/v1/submissions/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        problem_id: 1,
        language,
        code,
        test_cases: [{ input: stdin || '', expected_output: '' }],
      }),
    });

    if (res.ok) {
      const data = await res.json();
      const tc = data.test_cases?.[0];
      const stdout = tc?.actual_output ?? '';
      const stderr = tc?.error ?? '';
      return { stdout, stderr, output: stdout || stderr || '(no output)', error: null };
    }
  } catch (_) {
    // Judge Service not available, fall through to Flask fallback
  }

  // Fallback: Flask backend local executor
  try {
    const res = await fetch(`${BACKEND_API}/api/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ language, code, stdin }),
    });

    if (!res.ok) {
      const err = await res.text();
      return { stdout: '', stderr: '', output: '', error: `Execution error (${res.status}): ${err}` };
    }

    const data = await res.json();
    const stdout = data.stdout || '';
    const stderr = data.stderr || '';
    return { stdout, stderr, output: stdout || stderr || '(no output)', error: data.error };
  } catch (e) {
    return { stdout: '', stderr: '', output: '', error: `Network error: ${e.message}` };
  }
}
