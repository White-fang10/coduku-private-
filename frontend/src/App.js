import React, { useState, useEffect } from 'react';
import './App.css';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import CodeEditor from './pages/CodeEditor';
import Leaderboards from './pages/Leaderboards';
import Badges from './pages/Badges';
import AdminPanel from './pages/AdminPanel';
import TeacherDashboard from './pages/TeacherDashboard';
import HouseLogo from './components/HouseLogo';
import SortingCeremony from './pages/SortingCeremony';
import UserProfileModal from './components/UserProfileModal';
import GoldenSnitch from './components/GoldenSnitch';
import { CHARACTERS, CHAR_SRCS } from './data/characters';

const API = localStorage.getItem('NGROK_URL') || process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';
export { API };

// Returns true if this user hasn't seen the ceremony yet
// Teachers (and admins) never need the ceremony
function needsCeremony(userData) {
  if (!userData) return false;
  if (userData.role === 'teacher' || userData.role === 'admin') return false;
  // Only students who haven't completed the ceremony yet
  if (userData.role !== 'student') return false;
  const key = `ch_ceremony_done_${userData._id || userData.email}`;
  return !localStorage.getItem(key);
}
function markCeremonyDone(userData) {
  if (!userData) return;
  const key = `ch_ceremony_done_${userData._id || userData.email}`;
  localStorage.setItem(key, '1');
}

// Magical nav labels per role
const NAV_STUDENT = [
  { id: 'dashboard',    label: 'Dashboard' },
  { id: 'code',         label: 'Code Editor' },
  { id: 'leaderboards', label: 'Leaderboards' },
  { id: 'badges',       label: 'Badges' },
];
const NAV_ADMIN = [
  { id: 'dashboard',    label: 'Dashboard' },
  { id: 'code',         label: 'Code Editor' },
  { id: 'leaderboards', label: 'Leaderboards' },
  { id: 'badges',       label: 'Badges' },
  { id: 'admin',        label: 'Admin Panel' },
];
const NAV_TEACHER = [
  { id: 'dashboard', label: 'Progress Overview' },
  { id: 'leaderboards', label: 'House Leaderboards' },
  { id: 'teacher', label: 'Teacher Panel' },
];

const houseColors = {
  Gryffindor: '#ae0001',
  Hufflepuff: '#ecb939',
  Ravenclaw:  '#6375d6',
  Slytherin:  '#2a7c46',
};

function App() {
  const [user, setUser]         = useState(null);
  const [token, setToken]       = useState(null);
  const [page, setPage]         = useState('dashboard');
  const [loading, setLoading]   = useState(true);
  const [showIntro, setShowIntro]= useState(false);
  const [showCeremony, setShowCeremony] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [compDismissed, setCompDismissed] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem('ch_token');
    const savedUser  = localStorage.getItem('ch_user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      const parsedUser = JSON.parse(savedUser);
      // Restore saved character_id if present
      const charKey = `ch_character_id_${parsedUser._id || parsedUser.email}`;
      const savedCharId = localStorage.getItem(charKey);
      if (savedCharId && !parsedUser.character_id) {
        parsedUser.character_id = parseInt(savedCharId, 10);
      }
      setUser(parsedUser);
      if (parsedUser.role === 'teacher') setPage('dashboard');
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);
    localStorage.setItem('ch_token', accessToken);
    localStorage.setItem('ch_user', JSON.stringify(userData));
    if (userData.role === 'teacher') {
      setPage('dashboard');
      return;
    }
    if (needsCeremony(userData)) {
      setShowCeremony(true);
    } else {
      setShowIntro(true);
      setTimeout(() => setShowIntro(false), 2500);
      setPage('dashboard');
    }
  };

  const handleCeremonyComplete = async ({ house, character }) => {
    // Save character id to localStorage so the avatar persists across sessions
    const charKey = `ch_character_id_${user._id || user.email}`;
    localStorage.setItem(charKey, character.id);

    // Update user object with the ceremony-chosen house
    const updatedUser = { ...user, house, character_id: character.id };
    setUser(updatedUser);
    localStorage.setItem('ch_user', JSON.stringify(updatedUser));

    // Persist the chosen house to the backend
    try {
      await fetch(`${API}/api/user/set_house`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ house, character_id: character.id }),
      });
    } catch (e) {
      console.error('Failed to persist house to backend:', e);
    }

    markCeremonyDone(user);
    setShowCeremony(false);
    setPage('dashboard');
  };

  const [compStatus, setCompStatus] = useState({ active: false, question_id: null });

  useEffect(() => {
    const checkComp = async () => {
      try {
        const res = await fetch(`${API}/api/competition/status`);
        const data = await res.json();
        setCompStatus(data);
      } catch (e) {
        console.error("Comp check failed", e);
      }
    };
    if (user) checkComp();
  }, [user]);

  const handleLogout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('ch_token');
    localStorage.removeItem('ch_user');
    setPage('dashboard');
  };

  const enterCompetition = () => {
    setPage('code');
    const elem = document.documentElement;
    if (elem.requestFullscreen) elem.requestFullscreen();
    else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
    else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
  };

  if (loading) return (
    <div className="app-loader">
      <div className="loader-cauldron">
        <div className="cauldron-bubble" />
        <div className="cauldron-bubble" />
        <div className="cauldron-bubble" />
      </div>
      <p className="loader-text">Brewing your session…</p>
    </div>
  );

  if (!user || !token) return <AuthPage onLogin={handleLogin} />;

  if (showIntro && user?.role !== 'teacher') return (
    <div className="login-intro-overlay" style={{ '--house-color': houseColors[user.house] || '#6c3de8' }}>
      <div className="login-intro-content">
        <HouseLogo house={user.house} size={150} />
        <h1 className="login-intro-text">Welcome to {user.house || 'Hogwarts'}!</h1>
      </div>
    </div>
  );

  if (showCeremony && user?.role !== 'teacher') return <SortingCeremony onComplete={handleCeremonyComplete} />;

  const handleProfileUpdate = (newName, newCharId) => {
    const updatedUser = { ...user, name: newName, character_id: newCharId };
    setUser(updatedUser);
    localStorage.setItem('ch_user', JSON.stringify(updatedUser));
    const charKey = `ch_character_id_${user._id || user.email}`;
    localStorage.setItem(charKey, newCharId);
  };

  const navItems = user.role === 'teacher' ? NAV_TEACHER
    : user.role === 'admin' ? NAV_ADMIN
    : NAV_STUDENT;
  const houseColor = user.role === 'teacher' ? '#7c7c9a' : (houseColors[user.house] || '#6c3de8');

  const renderPage = () => {
    switch (page) {
      case 'dashboard':    return <Dashboard user={user} token={token} onNavigate={setPage} />;
      case 'code':         return <CodeEditor user={user} token={token} initialQuestionId={compStatus.active ? compStatus.question_id : null} competitionMode={compStatus.active} />;
      case 'leaderboards': return <Leaderboards user={user} token={token} />;
      case 'badges':       return <Badges user={user} token={token} />;
      case 'admin':        return user.role === 'admin' ? <AdminPanel user={user} token={token} /> : null;
      case 'teacher':      return user.role === 'teacher' ? <TeacherDashboard user={user} token={token} /> : null;
      default:             return user.role === 'teacher'
        ? <TeacherDashboard user={user} token={token} />
        : <Dashboard user={user} token={token} onNavigate={setPage} />;
    }
  };

  return (
    <div className="app" data-house={user.role === 'teacher' ? 'neutral' : (user.house || 'default')}>
      {/* Background Animated Logo — hidden for teachers */}
      {user.role !== 'teacher' && (
        <div className="bg-house-logo" aria-hidden="true">
          <HouseLogo house={user.house} size={800} />
        </div>
      )}

      {/* ── Harry Potter Fantasy Elements — hidden for teachers ── */}
      {user.role !== 'teacher' && <GoldenSnitch />}

      {/* Magical floating particles — hidden for teachers */}
      {user.role !== 'teacher' && (
        <div className="magic-particles" aria-hidden="true">
          {[...Array(12)].map((_, i) => (
            <span key={i} className="particle" style={{ '--i': i }} />
          ))}
        </div>
      )}

      {/* ── Navbar ── */}
      <nav className="navbar" style={{ '--house-color': houseColor }}>
        <div className="navbar-brand">
          {user.role === 'teacher'
            ? <span className="teacher-nav-icon">🎓</span>
            : <HouseLogo house={user.house} size={48} />
          }
          <span className="brand-name">Coduku</span>
        </div>

        <div className="navbar-links">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-btn ${page === item.id ? 'active' : ''}`}
              onClick={() => !compStatus.active && setPage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="navbar-user">
          <div 
            className="user-badge is-clickable" 
            style={{ borderColor: houseColor }}
            onClick={() => setShowProfileModal(true)}
            title="Customize Profile"
          >
            {user.character_id && CHAR_SRCS[user.character_id] ? (
              <img
                src={CHAR_SRCS[user.character_id]}
                alt="avatar"
                className="user-avatar user-avatar-img"
                style={{ borderColor: houseColor, background: houseColor }}
              />
            ) : (
              <span className="user-avatar" style={{ background: houseColor }}>
                {user.name.charAt(0).toUpperCase()}
              </span>
            )}
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-house" style={{ color: houseColor }}>{user.role === 'teacher' ? 'Teacher' : user.house}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Log Out</span>
          </button>
        </div>
      </nav>

      {/* ── Page Content ── */}
      <main className="main-content">
        {renderPage()}
      </main>

      {/* ── Competition Mode Overlay ── */}
      {compStatus.active && page !== 'code' && user.role !== 'teacher' && !compDismissed && (
        <div className="comp-overlay-lock">
          <div className="comp-lock-card card-glass">
            <h1 className="comp-lock-title">🧙‍♂️ Competition Active!</h1>
            <p className="comp-lock-msg">A special House Trial is underway ({compStatus.start_time} - {compStatus.end_time}).</p>
            <p className="comp-lock-sub">All House Ranks are currently frozen and decided ONLY by this competition.</p>
            <div className="comp-action-btns" style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '20px' }}>
              <button className="comp-start-btn" onClick={enterCompetition} style={{ padding: '0.8rem 1.5rem', fontSize: '1rem', flex: 1 }}>
                Enter Competition
              </button>
              <button className="btn btn-secondary" onClick={() => setCompDismissed(true)} style={{ padding: '0.8rem 1.5rem', flex: 1 }}>
                Take Later
              </button>
              <button className="btn btn-danger" onClick={() => setCompDismissed(true)} style={{ padding: '0.8rem 1.5rem', flex: 1 }}>
                Reject
              </button>
            </div>
            <p className="comp-lock-warning" style={{ marginTop: '15px' }}>Note: Fullscreen will be enforced during the trial.</p>
          </div>
        </div>
      )}

      {showProfileModal && (
        <UserProfileModal 
          user={user} 
          token={token} 
          onClose={() => setShowProfileModal(false)}
          onUpdate={handleProfileUpdate}
        />
      )}
    </div>
  );
}

export default App;
