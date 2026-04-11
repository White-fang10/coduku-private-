import React, { useState, useEffect } from 'react';
import './UserProfileModal.css';
import { CHARACTERS } from '../data/characters';
import { BADGE_CATEGORIES } from '../data/badges';

const API = process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

export default function UserProfileModal({ user, token, onClose, onUpdate }) {
  const [name, setName] = useState(user.name || '');
  const [charId, setCharId] = useState(user.character_id || null);
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${API}/api/user/profile`, { 
          headers: { Authorization: `Bearer ${token}` } 
        });
        const data = await res.json();
        
        // Merge dynamic badges (legacy) and claimed custom badges
        const dynamicBadges = data.badges || [];
        const claimedIds = data.claimed_badges || [];
        
        const allBadgeOptions = BADGE_CATEGORIES.flatMap(cat => cat.badges);
        const claimedBadges = allBadgeOptions.filter(b => claimedIds.includes(b.id));

        setBadges([...dynamicBadges, ...claimedBadges]);
      } catch (e) {
        console.error("Failed to fetch badges", e);
      }
    };
    fetchProfile();
  }, [token]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/user/update_profile`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ name, character_id: charId }),
      });
      if (res.ok) {
        onUpdate(name, charId);
        onClose();
      } else {
        alert("Failed to update profile");
      }
    } catch(e) {
      console.error(e);
      alert("Error updating profile");
    }
    setLoading(false);
  };

  return (
    <div className="profile-modal-overlay">
      <div className="profile-modal-content card-glass" style={{ '--house-color': '#6c3de8' }}>
        <h2 className="profile-modal-title">Customize Profile</h2>
        
        <div className="form-group">
          <label className="form-label">Name</label>
          <input 
            type="text" 
            className="input-field" 
            value={name} 
            onChange={e => setName(e.target.value)} 
            placeholder="Wizard Name"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Avatar</label>
          <div className="avatar-grid-wrapper">
             <div className="avatar-list">
               {CHARACTERS.map(c => (
                 <div 
                   key={c.id} 
                   className={`avatar-choice ${charId === c.id ? 'selected' : ''}`}
                   onClick={() => setCharId(c.id)}
                   style={{ '--char-color': c.color }}
                 >
                   <img src={c.src} alt={c.name} className="avatar-choice-img" />
                 </div>
               ))}
             </div>
          </div>
        </div>

        {user.role !== 'teacher' && (
          <div className="form-group">
            <label className="form-label">Your Badges</label>
            <div className="badges-list full-badges-mode">
              {badges.length === 0 ? (
                <p className="no-badges">No badges earned yet.</p>
              ) : (
                badges.map((b, idx) => (
                  <div key={b.id || idx} className={`mini-badge-v2 ${b.rarity?.toLowerCase() || ''}`} title={`${b.name}: ${b.givenFor || b.desc}`}>
                    <div className="mb-v2-glow" />
                    {b.image ? (
                      <img src={b.image} alt={b.name} className="mb-v2-img" />
                    ) : (
                      <span className="mb-v2-icon">{b.icon}</span>
                    )}
                    <div className="mb-v2-info">
                      <span className="mb-v2-name">{b.name}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>Close</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
}
