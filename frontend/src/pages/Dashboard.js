import React, { useState, useEffect, useCallback } from 'react';
import './Dashboard.css';
import './TeacherProgress.css';
import HouseLogo from '../components/HouseLogo';
import MagicalBadge from '../components/MagicalBadge';
import { Trophy, Code, Award, Zap, Compass, Star, Users, BarChart2, TrendingUp } from 'lucide-react';

const API = process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

const HOUSE_META = {
  Gryffindor: { color: '#ae0001', rank: 'Brave',   gradient: 'linear-gradient(135deg, rgba(174,0,1,0.2), transparent)' },
  Hufflepuff: { color: '#e8a800', rank: 'Loyal',   gradient: 'linear-gradient(135deg, rgba(232,168,0,0.2), transparent)' },
  Ravenclaw:  { color: '#4a5fa0', rank: 'Wise',    gradient: 'linear-gradient(135deg, rgba(74,95,160,0.2), transparent)' },
  Slytherin:  { color: '#2a7c46', rank: 'Cunning', gradient: 'linear-gradient(135deg, rgba(42,124,70,0.2), transparent)' },
};

// ── Teacher Progress Overview ─────────────────────────────────────────────
function TeacherProgressDashboard({ user, token, onNavigate }) {
  const [houses, setHouses]   = useState([]);
  const [global, setGlobal]   = useState([]);
  const [loading, setLoading] = useState(true);
  const headers = { Authorization: `Bearer ${token}` };

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [hRes, gRes] = await Promise.all([
        fetch(`${API}/api/leaderboards/houses`, { headers }),
        fetch(`${API}/api/leaderboards/global`, { headers }),
      ]);
      const [h, g] = await Promise.all([hRes.json(), gRes.json()]);
      setHouses(Array.isArray(h) ? h : []);
      setGlobal(Array.isArray(g) ? g : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading) return (
    <div className="dash-loader">
      <div className="loader-cauldron">
        <div className="cauldron-bubble" /><div className="cauldron-bubble" /><div className="cauldron-bubble" />
      </div>
      <p className="loader-text">Loading progress data…</p>
    </div>
  );

  const totalStudents  = houses.reduce((s, h) => s + (h.members || 0), 0);
  const totalSolved    = global.reduce((s, r) => s + (r.problems_solved || 0), 0);
  const avgScore       = global.length
    ? (global.reduce((s, r) => s + (r.average_score || 0), 0) / global.length).toFixed(1)
    : '0.0';
  const topHouse       = houses[0]?.house || '—';
  const maxScore       = houses[0]?.average_score || 1;

  // Best student per house from sorted global list
  const bestPerHouse = {};
  global.forEach(row => {
    if (row.house && !bestPerHouse[row.house]) bestPerHouse[row.house] = row;
  });

  const RANK_EMOJI  = ['🥇', '🥈', '🥉', '4th'];
  const RANK_STYLES = [
    { border: 'rgba(212,175,55,0.45)' },
    { border: 'rgba(192,192,192,0.4)' },
    { border: 'rgba(180,100,40,0.4)'  },
    { border: 'rgba(255,255,255,0.1)' },
  ];

  const summaryStats = [
    { label: 'Total Students',  value: totalStudents, icon: <Users size={20} />,    color: '#8b8bd8' },
    { label: 'Problems Solved', value: totalSolved,   icon: <Zap size={20} />,      color: '#6dbe8d' },
    { label: 'Class Avg Score', value: avgScore,      icon: <BarChart2 size={20} />, color: '#f0a050' },
    { label: 'Leading House',   value: topHouse,      icon: <Trophy size={20} />,   color: '#d4af37' },
  ];

  return (
    <div className="tp-root">
      {/* Header */}
      <div className="tp-header">
        <div className="tp-header-text">
          <h1 className="tp-title">Progress Overview</h1>
          <p className="tp-subtitle">Welcome, {user.name.split(' ')[0]}. Here's how all houses are performing.</p>
        </div>
        <div className="tp-header-actions">
          <button className="tp-btn-refresh" onClick={fetchAll} title="Refresh data">
            <TrendingUp size={14} /> Refresh
          </button>
          <button className="tp-btn-primary" onClick={() => onNavigate('leaderboards')}>
            <Trophy size={16} /> Full Leaderboard
          </button>
          <button className="tp-btn-secondary" onClick={() => onNavigate('teacher')}>
            <span>⚙️</span> Teacher Panel
          </button>
        </div>
      </div>

      {/* Summary stats */}
      <div className="tp-stats-grid">
        {summaryStats.map(s => (
          <div key={s.label} className="tp-stat-card" style={{ '--scolor': s.color }}>
            <div className="tp-stat-icon" style={{ color: s.color }}>{s.icon}</div>
            <div className="tp-stat-value">{s.value}</div>
            <div className="tp-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* House Rankings */}
      <div className="tp-section-title">
        <TrendingUp size={18} /> House Rankings
      </div>
      <div className="tp-houses-grid">
        {houses.map((h, i) => {
          const m    = HOUSE_META[h.house] || { color: '#6c3de8' };
          const pct  = Math.min(100, ((h.average_score || 0) / maxScore) * 100);
          const best = bestPerHouse[h.house];
          const rs   = RANK_STYLES[i] || RANK_STYLES[3];
          return (
            <div
              key={h.house}
              className="tp-house-card"
              style={{ '--hcolor': m.color, borderColor: rs.border }}
            >
              <div className="tp-house-rank-badge">{RANK_EMOJI[i] || `#${i + 1}`}</div>
              <div className="tp-house-logo">
                <HouseLogo house={h.house} size={56} />
              </div>
              <h3 className="tp-house-name" style={{ color: m.color }}>{h.house}</h3>
              <div className="tp-house-stats">
                <div className="tp-house-stat">
                  <span className="tp-hs-val">{h.average_score?.toFixed(1)}</span>
                  <span className="tp-hs-lbl">Avg Score</span>
                </div>
                <div className="tp-house-stat">
                  <span className="tp-hs-val">{h.members ?? 0}</span>
                  <span className="tp-hs-lbl">Members</span>
                </div>
                <div className="tp-house-stat">
                  <span className="tp-hs-val">{h.total_score?.toFixed(0) ?? 0}</span>
                  <span className="tp-hs-lbl">Total Pts</span>
                </div>
              </div>
              <div className="tp-house-bar-track">
                <div className="tp-house-bar-fill" style={{ width: `${pct}%`, background: m.color }} />
              </div>
              {best && (
                <div className="tp-house-best" style={{ borderColor: m.color + '44' }}>
                  <span className="tp-best-label">⭐ Top Student</span>
                  <span className="tp-best-name">{best.name}</span>
                  <span className="tp-best-score" style={{ color: m.color }}>{best.average_score?.toFixed(1)} pts</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Student Leaderboard */}
      <div className="tp-section-title">
        <Star size={18} /> Student Leaderboard — Top {Math.min(20, global.length)}
      </div>
      <div className="tp-table-wrap">
        <table className="tp-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Name</th>
              <th>House</th>
              <th>Avg Score</th>
              <th>Solved</th>
              <th>Submissions</th>
            </tr>
          </thead>
          <tbody>
            {global.slice(0, 20).map(row => {
              const m = HOUSE_META[row.house] || {};
              return (
                <tr key={row.rank} className="tp-table-row">
                  <td className="tp-rank-cell">
                    {row.rank <= 3
                      ? <span className="tp-medal">{['🥇','🥈','🥉'][row.rank - 1]}</span>
                      : `#${row.rank}`}
                  </td>
                  <td className="tp-name-cell">{row.name}</td>
                  <td>
                    <span
                      className="tp-house-tag"
                      style={{ color: m.color || '#a78bfa', background: (m.color || '#6c3de8') + '22' }}
                    >
                      {row.house}
                    </span>
                  </td>
                  <td className="tp-score-cell">{row.average_score?.toFixed(1)}</td>
                  <td>{row.problems_solved}</td>
                  <td className="tp-subs-cell">{row.submissions}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {global.length === 0 && <p className="tp-empty">No student data yet.</p>}
      </div>
    </div>
  );
}

// ── Student Dashboard ─────────────────────────────────────────────────────
export default function Dashboard({ user, token, onNavigate }) {
  const [profile, setProfile]     = useState(null);
  const [houses, setHouses]       = useState([]);
  const [recentSubs, setRecent]   = useState([]);
  const [loading, setLoading]     = useState(true);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [pRes, hRes, sRes] = await Promise.all([
        fetch(`${API}/api/user/profile`, { headers }),
        fetch(`${API}/api/leaderboards/houses`, { headers }),
        fetch(`${API}/api/user/submissions`, { headers }),
      ]);
      const [p, h, s] = await Promise.all([pRes.json(), hRes.json(), sRes.json()]);
      setProfile(p);
      setHouses(Array.isArray(h) ? h : []);
      setRecent(Array.isArray(s) ? s.slice(0, 5) : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Route teachers to their own view
  if (user.role === 'teacher') {
    return <TeacherProgressDashboard user={user} token={token} onNavigate={onNavigate} />;
  }

  const meta = HOUSE_META[user.house] || { color: '#6c3de8', rank: 'Apprentice', gradient: 'linear-gradient(135deg, rgba(108,61,232,0.2), transparent)' };

  if (loading) return (
    <div className="dash-loader">
      <div className="loader-cauldron">
        <div className="cauldron-bubble" /><div className="cauldron-bubble" /><div className="cauldron-bubble" />
      </div>
      <p className="loader-text">Loading...</p>
    </div>
  );

  const stats = [
    { label: 'Problems Solved',   value: profile?.problems_solved ?? 0,    icon: <Zap size={20} /> },
    { label: 'Average Score',     value: `${profile?.average_score ?? 0}`, icon: <Star size={20} /> },
    { label: 'Total Submissions', value: profile?.total_submissions ?? 0,  icon: <Compass size={20} /> },
    { label: 'House Rank',        value: meta.rank,                        icon: <Trophy size={20} /> },
  ];

  return (
    <div className="dashboard">
      <div className="dash-hero card-glass" style={{ backgroundImage: meta.gradient, borderColor: meta.color }}>
        <div className="hero-text">
          <h1 className="hero-greeting">Welcome back, {user.name.split(' ')[0]}!</h1>
          <p className="hero-sub">Welcome to your Coding Dashboard.</p>
        </div>
        <div className="hero-house-icon">
          <HouseLogo house={user.house} size={140} />
        </div>
      </div>

      <div className="stats-grid">
        {stats.map(s => (
          <div key={s.label} className="stat-card card-glass">
            <div className="stat-icon-wrap" style={{ color: meta.color }}>
              <span className="stat-icon">{s.icon}</span>
            </div>
            <div className="stat-content">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="dash-body">
        <div className="dash-left">
          <div className="card house-standings">
            <div className="section-header">
              <h2 className="section-title">House Standings</h2>
              <button className="view-all-btn" onClick={() => onNavigate('leaderboards')}>View Leaderboards</button>
            </div>
            <div className="house-list">
              {houses.map((h, i) => {
                const m = HOUSE_META[h.house] || { color: '#6c3de8' };
                const isFirst = i === 0;
                const isUserHouse = h.house === user.house;
                return (
                  <div key={h.house} className={`house-row ${isUserHouse ? 'my-house' : ''}`}>
                    <span className={`house-rank ${isFirst ? 'rank-first' : ''}`}>#{i + 1}</span>
                    <div className="house-icon-sm"><HouseLogo house={h.house} size={36} /></div>
                    <div className="house-bar-wrap">
                      <div className="house-bar-label">
                        <span className="house-name" style={{ color: m.color }}>{h.house} {isUserHouse && '(You)'}</span>
                        <span className="house-bar-score">{h.average_score.toFixed(1)} pts</span>
                      </div>
                      <div className="house-bar-track">
                        <div
                          className="house-bar-fill"
                          style={{ width: `${Math.min(100, (h.average_score / (houses[0]?.average_score || Math.max(1, h.average_score))) * 100)}%`, background: m.color }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="achievements-card card-glass">
            <div className="achievements-header">
              <Award className="card-icon-gold" />
              <h2 className="card-title">Magical Achievements</h2>
            </div>
            <p className="card-sub">Badges earned through your coding trials.</p>
            <div className="badge-grid">
              {profile?.badges && profile.badges.map((b, i) => (
                <div key={i} className="badge-item scale-up">
                  <MagicalBadge type={b.id || b} size="md" />
                </div>
              ))}
              {(!profile?.badges || profile.badges.length === 0) && (
                <div className="no-badges-msg">
                  <span className="crystal-ball">🔮</span>
                  <p>Your future achievements are yet to be revealed.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="dash-right">
          <div className="card quick-actions">
            <h2 className="section-title">Quick Links</h2>
            <div className="quick-links">
              <button className="q-link-item" onClick={() => onNavigate('code')}>
                <Code size={20} /><span>Full Practice</span>
              </button>
              <button className="q-link-item glow-primary" onClick={() => onNavigate('code')}>
                <Star size={20} /><span>Enter Test (Active 5-10PM)</span>
              </button>
              <button className="q-link-item" onClick={() => onNavigate('leaderboards')}>
                <Trophy size={20} /><span>Leaderboards</span>
              </button>
              {user.role === 'admin' && (
                <button className="q-link-item" onClick={() => onNavigate('admin')}>
                  <span className="action-icon">≡</span><span>Admin Panel</span>
                </button>
              )}
            </div>
          </div>

          <div className="card recent-subs">
            <h2 className="section-title">Recent Submissions</h2>
            {recentSubs.length === 0
              ? <p className="empty-state">No submissions yet. Visit the Code Editor!</p>
              : (
                <div className="sub-list">
                  {recentSubs.map(s => (
                    <div key={s._id} className="sub-row">
                      <div className="sub-info">
                        <span className="sub-title">{s.question_title}</span>
                        <span className={`badge badge-${(s.difficulty || '').toLowerCase()}`}>{s.difficulty}</span>
                      </div>
                      <div className="sub-meta">
                        <span className="sub-score" style={{ color: s.score >= 80 ? 'var(--success)' : s.score >= 50 ? 'var(--warning)' : 'var(--error)' }}>
                          {s.score?.toFixed(1) ?? '0'} pts
                        </span>
                        <span className="sub-tests">{s.passed_tests}/{s.total_tests} pass</span>
                      </div>
                    </div>
                  ))}
                </div>
              )
            }
          </div>
        </div>
      </div>
    </div>
  );
}
