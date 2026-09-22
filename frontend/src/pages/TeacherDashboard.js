import React, { useState, useEffect, useCallback } from 'react';
import './AdminPanel.css';

const API = localStorage.getItem('NGROK_URL') || process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

const EMPTY_TC = { input: '', output: '', function_name: 'solution' };
const EMPTY_Q  = {
  title: '', description: '', difficulty: 'Easy',
  time_limit: 5, memory_limit: 256, solution: '', test_cases: [{ ...EMPTY_TC }],
};

export default function TeacherDashboard({ user, token }) {
  const [tab, setTab]           = useState('questions');
  const [questions, setQuestions]= useState([]);
  const [compQId, setCompQId]   = useState(null);
  const [compStart, setCompStart]= useState('17:00');
  const [compEnd, setCompEnd]   = useState('22:00');
  const [form, setForm]         = useState({ ...EMPTY_Q, test_cases: [{ ...EMPTY_TC }] });
  const [editId, setEditId]     = useState(null);
  const [saving, setSaving]     = useState(false);
  const [msg, setMsg]           = useState('');
  const [error, setError]       = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const fetchQuestions = useCallback(async () => {
    try {
      const res  = await fetch(`${API}/api/questions`, { headers });
      const data = await res.json();
      setQuestions(Array.isArray(data) ? data : []);
    } catch (e) {}
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const fetchComp = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/competition/status`);
      const data = await res.json();
      setCompQId(data.question_id);
      if (data.start_time) setCompStart(data.start_time);
      if (data.end_time) setCompEnd(data.end_time);
    } catch (e) {}
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { 
    fetchQuestions();
    fetchComp();
  }, [fetchQuestions, fetchComp]);

  // ── Form helpers ──────────────────────────────────────────────────────────
  const updateField = (field, val) => setForm(f => ({ ...f, [field]: val }));

  const updateTC = (i, field, val) => setForm(f => {
    const tcs = [...f.test_cases];
    tcs[i] = { ...tcs[i], [field]: val };
    return { ...f, test_cases: tcs };
  });

  const addTC    = () => setForm(f => ({ ...f, test_cases: [...f.test_cases, { ...EMPTY_TC }] }));
  const removeTC = (i) => setForm(f => ({ ...f, test_cases: f.test_cases.filter((_, idx) => idx !== i) }));

  const startEdit = (q) => {
    setEditId(q._id);
    setForm({
      title: q.title, description: q.description, difficulty: q.difficulty,
      time_limit: q.time_limit, memory_limit: q.memory_limit,
      solution: q.solution || '',
      test_cases: q.test_cases?.length ? q.test_cases : [{ ...EMPTY_TC }],
    });
    setTab('create');
  };
  const cancelEdit = () => { setEditId(null); setForm({ ...EMPTY_Q, test_cases: [{ ...EMPTY_TC }] }); };

  const assignCompetition = async (qId) => {
    setMsg(''); setError('');
    try {
      const res = await fetch(`${API}/api/admin/competition`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: qId, start_time: compStart, end_time: compEnd }),
      });
      if (!res.ok) throw new Error('Assignment failed');
      setCompQId(qId);
      setMsg(`🏆 Competition problem assigned successfully for ${compStart} to ${compEnd}!`);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setMsg(''); setError('');

    // Parse inputs: try JSON first, fallback to string
    const parsedTCs = form.test_cases.map(tc => {
      let inp = tc.input;
      let out = tc.output;
      try { inp = JSON.parse(tc.input); } catch (_) {}
      try { out = JSON.parse(tc.output); } catch (_) {}
      return { input: inp, output: out, function_name: tc.function_name || 'solution' };
    });

    const payload = {
      ...form,
      time_limit: Number(form.time_limit),
      memory_limit: Number(form.memory_limit),
      test_cases: parsedTCs,
    };

    setSaving(true);
    try {
      const url    = editId ? `${API}/api/admin/questions/${editId}` : `${API}/api/admin/questions`;
      const method = editId ? 'PUT' : 'POST';
      const res    = await fetch(url, {
        method,
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Save failed');
      setMsg(editId ? '✅ Problem updated!' : '✅ Problem created!');
      cancelEdit();
      fetchQuestions();
      setTab('questions');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const diffClass = (d) => ({ Easy: 'badge-easy', Medium: 'badge-medium', Hard: 'badge-hard' }[d] || '');

  return (
    <div className="admin-root">
      <h1 className="page-title">Teacher Dashboard</h1>
      <p className="page-subtitle">Upload questions and define test cases for your students.</p>

      <div className="admin-tabs">
        {[
          { id: 'questions',    label: '📋 Problems' },
          { id: 'create',       label: editId ? '✏️ Edit Problem' : '➕ Add Problem' },
          { id: 'assign',       label: '🏆 Assign Test' },
        ].map(t => (
          <button
            key={t.id}
            className={`admin-tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => { if (t.id !== 'create') cancelEdit(); setTab(t.id); setMsg(''); setError(''); }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {msg   && <div className="admin-msg success">{msg}</div>}
      {error && <div className="admin-msg error">⚠️ {error}</div>}

      {/* ── Question list ── */}
      {tab === 'questions' && (
        <div className="card">
          <div className="admin-list-header">
            <span className="ql-count">{questions.length} problem{questions.length !== 1 ? 's' : ''}</span>
            <button className="btn btn-primary" onClick={() => setTab('create')}>➕ Add Problem</button>
          </div>
          {questions.length === 0
            ? <p className="admin-empty">No problems yet. Create one!</p>
            : (
              <table className="admin-table">
                <thead><tr><th>Title</th><th>Difficulty</th><th>Time Limit</th><th>Actions</th></tr></thead>
                <tbody>
                  {questions.map(q => (
                    <tr key={q._id}>
                      <td className="qt-title">{q.title}</td>
                      <td><span className={`badge ${diffClass(q.difficulty)}`}>{q.difficulty}</span></td>
                      <td>{q.time_limit}s</td>
                      <td>
                        <button className="btn btn-secondary btn-sm" onClick={() => startEdit(q)}>✏️ Edit</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          }
        </div>
      )}

      {/* ── Assign Competition ── */}
      {tab === 'assign' && (
        <div className="card">
          <h2 className="section-header">Select Competition Question</h2>
          <p className="section-sub">Choose which problem will be the exclusive trial for the specified window.</p>
          <div className="admin-list-header" style={{flexWrap: 'wrap', gap: '1rem'}}>
            <span className="ql-count">Current Active ID: {compQId || 'None'}</span>
            <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
              <label style={{color: '#a8a8b3', fontSize: '0.85rem'}}>From:
                <input type="time" value={compStart} onChange={e => setCompStart(e.target.value)} style={{marginLeft: '0.5rem', background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none', padding: '0.2rem', borderRadius: '5px'}}/>
              </label>
              <label style={{color: '#a8a8b3', fontSize: '0.85rem'}}>To:
                <input type="time" value={compEnd} onChange={e => setCompEnd(e.target.value)} style={{marginLeft: '0.5rem', background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none', padding: '0.2rem', borderRadius: '5px'}}/>
              </label>
            </div>
          </div>
          <table className="admin-table">
            <thead><tr><th>Title</th><th>Difficulty</th><th>Action</th></tr></thead>
            <tbody>
              {questions.map(q => (
                <tr key={q._id}>
                  <td>{q.title}</td>
                  <td><span className={`badge ${diffClass(q.difficulty)}`}>{q.difficulty}</span></td>
                  <td>
                    {compQId === q._id 
                      ? <button className="btn btn-success btn-sm btn-disabled" disabled>Active</button>
                      : <button className="btn btn-primary btn-sm" onClick={() => assignCompetition(q._id)}>Assign</button>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Create / Edit form ── */}
      {tab === 'create' && (
        <form className="admin-form card" onSubmit={handleSave}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input className="input-field" value={form.title} onChange={e => updateField('title', e.target.value)} placeholder="Two Sum" required />
            </div>
            <div className="form-group">
              <label className="form-label">Difficulty *</label>
              <select className="input-field" value={form.difficulty} onChange={e => updateField('difficulty', e.target.value)}>
                <option>Easy</option><option>Medium</option><option>Hard</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Description *</label>
            <textarea
              className="input-field admin-desc"
              value={form.description}
              onChange={e => updateField('description', e.target.value)}
              placeholder="Describe the problem clearly…"
              rows={4}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Time Limit (seconds)</label>
              <input className="input-field" type="number" min="1" max="30" value={form.time_limit} onChange={e => updateField('time_limit', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Memory Limit (MB)</label>
              <input className="input-field" type="number" min="16" max="512" value={form.memory_limit} onChange={e => updateField('memory_limit', e.target.value)} />
            </div>
          </div>

          {/* Test cases */}
          <div className="tc-section">
            <div className="tc-header">
              <h3 className="tc-title">🧪 Test Cases</h3>
              <button type="button" className="btn btn-secondary btn-sm" onClick={addTC}>+ Add</button>
            </div>
            {form.test_cases.map((tc, i) => (
              <div key={i} className="tc-row">
                <div className="tc-row-header">
                  <span className="tc-num">Test {i + 1}</span>
                  {form.test_cases.length > 1 && (
                    <button type="button" className="btn btn-danger btn-sm" onClick={() => removeTC(i)}>✕ Remove</button>
                  )}
                </div>
                <div className="tc-fields">
                  <div className="form-group">
                    <label className="form-label">Input (JSON or value)</label>
                    <input className="input-field" value={tc.input} onChange={e => updateTC(i, 'input', e.target.value)} placeholder='[2,7,11,15], 9' />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Expected Output</label>
                    <input className="input-field" value={tc.output} onChange={e => updateTC(i, 'output', e.target.value)} placeholder='[0,1]' />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Function Name</label>
                    <input className="input-field" value={tc.function_name} onChange={e => updateTC(i, 'function_name', e.target.value)} placeholder="solution" />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Reference solution (optional) */}
          <div className="form-group">
            <label className="form-label">Reference Solution (optional)</label>
            <textarea
              className="input-field code-area admin-solution"
              value={form.solution}
              onChange={e => updateField('solution', e.target.value)}
              placeholder="def solution(*args): ..."
              rows={5}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => { cancelEdit(); setTab('questions'); }}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? '⏳ Saving…' : editId ? '💾 Update Problem' : '✅ Create Problem'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
