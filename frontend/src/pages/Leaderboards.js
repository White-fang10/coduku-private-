import React, { useState, useEffect, useCallback } from 'react';
import './Leaderboards.css';
import HouseLogo from '../components/HouseLogo';
import { X } from 'lucide-react';
import { BADGE_CATEGORIES } from '../data/badges';
import { CHAR_SRCS } from '../data/characters';

const API = localStorage.getItem('NGROK_URL') || process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

const HOUSE_META = {
  Gryffindor: { color: '#ae0001', icon: '', gradient: 'linear-gradient(135deg,#ae0001,#d4af37)' },
  Hufflepuff:  { color: '#ecb939', icon: '', gradient: 'linear-gradient(135deg,#ecb939,#e8832a)' },
  Ravenclaw:   { color: '#6375d6', icon: '', gradient: 'linear-gradient(135deg,#222f5b,#6375d6)' },
  Slytherin:   { color: '#2a7c46', icon: '', gradient: 'linear-gradient(135deg,#1a472a,#5d8a5e)' },
};

export default function Leaderboards({ user, token }) {
  const [tab, setTab]             = useState('global');   // 'global' | 'houses' | house name
  const [global, setGlobal]       = useState([]);
  const [houses, setHouses]       = useState([]);
  const [houseMembers, setMembers]= useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading]     = useState(true);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [gRes, hRes] = await Promise.all([
        fetch(`${API}/api/leaderboards/global`, { headers }),
        fetch(`${API}/api/leaderboards/houses`, { headers }),
      ]);
      const [g, h] = await Promise.all([gRes.json(), hRes.json()]);
      setGlobal(Array.isArray(g) ? g : []);
      setHouses(Array.isArray(h) ? h : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const viewHouse = async (houseName) => {
    setTab(houseName);
    setLoading(true);
    try {
      const res  = await fetch(`${API}/api/leaderboards/house/${houseName}`, { headers });
      const data = await res.json();
      setMembers(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchPlayerDetails = async (uid) => {
    try {
      const res = await fetch(`${API}/api/user/profile/${uid}`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (!data.error) setSelectedPlayer(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const rankMedal = (r) => r === 1 ? '1st' : r === 2 ? '2nd' : r === 3 ? '3rd' : `#${r}`;

  const isTeacher = user.role === 'teacher';

  return (
    <div className="lb-root">
      <h1 className="page-title">{isTeacher ? 'House Leaderboards' : 'Leaderboards'}</h1>
      <p className="page-subtitle">
        {isTeacher
          ? 'Monitor student performance across all houses.'
          : 'See how you and your house stack up against the competition.'}
      </p>

      {/* Tabs */}
      <div className="lb-tabs">
        <button className={`lb-tab ${tab === 'global' ? 'active' : ''}`} onClick={() => setTab('global')}>
          Global
        </button>
        <button className={`lb-tab ${tab === 'houses' ? 'active' : ''}`} onClick={() => setTab('houses')}>
          Houses
        </button>
        {Object.values(HOUSE_META).map((m, i) => {
          const name = Object.keys(HOUSE_META)[i];
          return (
            <button
              key={name}
              className={`lb-tab ${tab === name ? 'active' : ''}`}
              style={tab === name ? { borderColor: m.color, color: m.color } : {}}
              onClick={() => viewHouse(name)}
            >
              {m.icon} {name}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="lb-loading">
          <div className="loader-spinner"></div>
          <p>Loading leaderboard…</p>
        </div>
      ) : (
        <>
          {/* ── Global ── */}
          {tab === 'global' && (
            <div className="lb-table-wrap card">
              <table className="lb-table">
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
                  {global.map(row => {
                    const m = HOUSE_META[row.house] || {};
                    const isMe = user.role !== 'teacher' && row.name === user.name;
                    return (
                      <tr key={row.rank} className={`${isMe ? 'my-row' : ''} clickable-row`} onClick={() => fetchPlayerDetails(row.id)}>
                        <td className="rank-cell">{rankMedal(row.rank)}</td>
                        <td className="name-cell">
                          {row.name}
                          {isMe && <span className="you-badge">YOU</span>}
                        </td>
                        <td>
                          <span className="house-tag" style={{ color: m.color || '#a78bfa' }}>
                            {m.icon} {row.house}
                          </span>
                        </td>
                        <td className="score-cell">{row.average_score?.toFixed(1)}</td>
                        <td>{row.problems_solved}</td>
                        <td>{row.submissions}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {global.length === 0 && <p className="lb-empty">No students yet.</p>}
            </div>
          )}

          {/* ── Houses ── */}
          {tab === 'houses' && (
            <div className="houses-grid">
              {houses.map(h => {
                const m = HOUSE_META[h.house] || { color: '#6c3de8', icon: '', gradient: 'linear-gradient(135deg,#6c3de8,#a78bfa)' };
                return (
                  <div
                    key={h.house}
                    className="house-card"
                    style={{ '--hcolor': m.color }}
                    onClick={() => viewHouse(h.house)}
                  >
                    <div className="house-card-bg" style={{ background: m.gradient }} />
                    <div className="house-card-content">
                      <div className="hc-rank">{rankMedal(h.rank)}</div>
                      <div className="hc-icon"><HouseLogo house={h.house} size={70} /></div>
                      <h3 className="hc-name">{h.house}</h3>
                      <div className="hc-score">{h.average_score?.toFixed(1)} <span>pts avg</span></div>
                      <div className="hc-meta">
                        <span>{h.members} members</span>
                        <span>{h.total_score?.toFixed(0)} total</span>
                      </div>
                      <button className="hc-view-btn">View Members →</button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ── House Members ── */}
          {!['global', 'houses'].includes(tab) && (
            <>
              <div className="house-member-header">
                <div className="house-back" onClick={() => setTab('houses')}>← Houses</div>
                <h2 style={{ color: HOUSE_META[tab]?.color }}>
                  {HOUSE_META[tab]?.icon} {tab} Members
                </h2>
              </div>
              <div className="lb-table-wrap card">
                <table className="lb-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Name</th>
                      <th>Avg Score</th>
                      <th>Solved</th>
                      <th>Submissions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {houseMembers.map(row => {
                      const isMe = user.role !== 'teacher' && row.name === user.name;
                      return (
                        <tr key={row.rank} className={`${isMe ? 'my-row' : ''} clickable-row`} onClick={() => fetchPlayerDetails(row.id)}>
                          <td className="rank-cell">{rankMedal(row.rank)}</td>
                          <td className="name-cell">
                            {row.name}
                            {isMe && <span className="you-badge">YOU</span>}
                          </td>
                          <td className="score-cell">{row.average_score?.toFixed(1)}</td>
                          <td>{row.problems_solved}</td>
                          <td>{row.submissions}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {houseMembers.length === 0 && <p className="lb-empty">No members yet.</p>}
              </div>
            </>
          )}
        </>
      )}

      {/* ── Player Profile Modal ── */}
      {selectedPlayer && !selectedPlayer.error && (
        <div className="profile-detail-overlay">
          <div className="profile-detail-card card-glass">
            <button className="close-btn" onClick={() => setSelectedPlayer(null)}>
              <X size={24} />
            </button>
            <div className="p-detail-header">
              <div className="p-logo-wrapper">
                <HouseLogo house={selectedPlayer.house} size={90} />
              </div>
              
              {selectedPlayer.character_id && CHAR_SRCS[selectedPlayer.character_id] && (
                <div className="p-detail-char-wrap">
                  <div className="p-detail-char-glow" style={{'--hcolor': HOUSE_META[selectedPlayer.house]?.color || '#6c3de8'}} />
                  <img 
                    src={CHAR_SRCS[selectedPlayer.character_id]} 
                    alt="Character" 
                    className="p-detail-char-img" 
                  />
                </div>
              )}

              <h2 className="p-detail-name">{selectedPlayer.name}</h2>
              <span className="p-detail-house">{selectedPlayer.house} House</span>
            </div>
            
            <div className="p-detail-stats">
              <div className="p-stat">
                <span className="p-stat-val">{selectedPlayer.problems_solved}</span>
                <span className="p-stat-lbl">Points</span>
              </div>
              <div className="p-stat">
                <span className="p-stat-val">{selectedPlayer.streak}</span>
                <span className="p-stat-lbl">Streak</span>
              </div>
            </div>

            {/* Hide badges section for teachers */}
            {user.role !== 'teacher' && (
              <div className="p-detail-badges">
                <h3 className="p-badges-title">Magical Awards</h3>
                <div className="p-badge-list">
                  {/* Dynamic Legacy Badges */}
                  {selectedPlayer.badges?.map((b, i) => (
                    <div key={`leg-${i}`} className="lb-mini-badge legacy" title={b.desc}>
                      <span className="lb-mb-icon">{b.icon}</span>
                      <span className="lb-mb-name">{b.name}</span>
                    </div>
                  ))}
                  
                  {/* Claimed Custom Badges */}
                  {(() => {
                    const claimedIds = selectedPlayer.claimed_badges || [];
                    const allBadgeOptions = BADGE_CATEGORIES.flatMap(cat => cat.badges);
                    const claimed = allBadgeOptions.filter(b => claimedIds.includes(b.id));
                    
                    return claimed.map((b, i) => (
                      <div key={`custom-${i}`} className={`lb-mini-badge ${b.rarity?.toLowerCase()}`} title={b.givenFor}>
                        <div className="lb-mb-glow" style={{'--rarity-color': b.color}} />
                        {b.image ? (
                          <img src={b.image} alt={b.name} className="lb-mb-img" />
                        ) : (
                          <span className="lb-mb-icon">{b.icon}</span>
                        )}
                        <span className="lb-mb-name">{b.name}</span>
                      </div>
                    ));
                  })()}

                  {(!selectedPlayer.badges || selectedPlayer.badges.length === 0) && 
                   (!selectedPlayer.claimed_badges || selectedPlayer.claimed_badges.length === 0) && (
                    <p className="p-no-badges">No badges yet.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
