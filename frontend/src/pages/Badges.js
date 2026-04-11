import React, { useState, useEffect } from 'react';
import './Badges.css';
import AdvancedBadgeArt from '../components/AdvancedBadgeArt';
import { BADGE_CATEGORIES, RARITY_META } from '../data/badges';

const API = process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

/* ── Components ──────────────────────────────────────────────────── */
function RarityStars({ rarity }) {
  const meta = RARITY_META[rarity] || RARITY_META.Common;
  return (
    <span className="rarity-stars" style={{ color: meta.color }}>
      {'★'.repeat(meta.stars)}{'☆'.repeat(Math.max(0, 5 - meta.stars))}
    </span>
  );
}

function BadgeCard({ badge, index, categoryId, userProfile, onClaim }) {
  const [hovered, setHovered] = useState(false);
  const rm = RARITY_META[badge.rarity] || RARITY_META.Common;
  
  const isUnlocked = userProfile?.unlocked_badges?.includes(badge.id) || false;
  const isClaimed = userProfile?.claimed_badges?.includes(badge.id) || false;

  const canClaim = isUnlocked && !isClaimed;

  return (
    <div
      className={`badge-card ${badge.rarity.toLowerCase()} ${hovered ? 'hovered' : ''} ${!isUnlocked ? 'badge-locked' : ''} ${canClaim ? 'badge-can-claim' : ''}`}
      style={{
        '--badge-color': badge.color,
        '--badge-border': rm.border,
        '--badge-bg': rm.bg,
        animationDelay: `${index * 0.06}s`
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Glow blob */}
      <div className="badge-card-glow" />

      {/* Rarity ribbon */}
      <div className="rarity-ribbon" style={{ background: rm.color }}>
        {badge.rarity}
      </div>

      {/* Icon area */}
      <div className="badge-card-icon-wrap" style={{ position: 'relative', zIndex: 5, marginTop: '1rem', marginBottom: '0.5rem' }}>
        {badge.image ? (
          <img src={badge.image} alt={badge.name} style={{ width: 160, height: 160, objectFit: 'contain', mixBlendMode: 'screen', filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.2))' }} />
        ) : (
          <AdvancedBadgeArt badgeId={badge.id} rarity={badge.rarity} category={categoryId} size={160} />
        )}
        
        <div className="badge-card-particles">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="badge-particle" style={{ '--i': i }} />
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="badge-card-info">
        <h3 className="badge-card-name">{badge.name}</h3>
        <RarityStars rarity={badge.rarity} />
        <p className="badge-card-for">
          <span className="for-label">For:</span> {badge.givenFor}
        </p>
        <p className="badge-card-design">{badge.design}</p>
      </div>

      {/* Series tag if present */}
      {badge.series && (
        <div className="badge-series-tag">{badge.series}</div>
      )}

      {canClaim && (
        <button 
          className="badge-claim-btn"
          onClick={(e) => { e.stopPropagation(); onClaim(badge); }}
        >
          ✨ Claim Magic ✨
        </button>
      )}
      {!isUnlocked && (
        <div className="badge-lock-overlay">
          <span className="lock-icon">🔒</span>
        </div>
      )}
    </div>
  );
}

function CategorySection({ category, userProfile, onClaim }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <section className="badge-category" style={{ '--cat-color': category.accentColor, '--cat-gradient': category.gradientFrom }}>
      <div className="badge-category-header" onClick={() => setExpanded(e => !e)}>
        <div className="badge-cat-left">
          <span className="cat-icon">{category.icon}</span>
          <div>
            <h2 className="cat-title">
              {category.title}
              <span className="cat-count">{category.badges.length}</span>
            </h2>
            <p className="cat-subtitle">{category.subtitle}</p>
          </div>
        </div>
        <div className="cat-header-right">
          <span className="cat-series">{category.seriesName}</span>
          <button className="cat-toggle">{expanded ? '▲' : '▼'}</button>
        </div>
      </div>

      {expanded && (
        <div className="badge-cards-grid">
          {category.badges.map((badge, i) => (
            <BadgeCard key={badge.id} badge={badge} index={i} categoryId={category.id} userProfile={userProfile} onClaim={onClaim} />
          ))}
        </div>
      )}
    </section>
  );
}

function ClaimBadgeModal({ badge, onClose }) {
  if (!badge) return null;
  return (
    <div className="claim-modal-overlay">
      <div className="claim-modal-content">
        <div className="claim-rays" />
        <div className="claim-particles">
          {[...Array(15)].map((_, i) => <div key={i} className="claim-particle" style={{ '--i': i }} />)}
        </div>
        <h2 className="claim-title">Achievement Unlocked!</h2>
        <div className="claim-badge-showcase">
          <div className="claim-badge-glow" style={{'--badge-color': RARITY_META[badge.rarity]?.color || '#fff'}}></div>
          {badge.image ? (
            <img src={badge.image} alt={badge.name} className="claim-badge-img" draggable={false} />
          ) : (
            <div className="claim-badge-img"><AdvancedBadgeArt badgeId={badge.id} rarity={badge.rarity} size={200} /></div>
          )}
        </div>
        <h3 className="claim-badge-name">{badge.name}</h3>
        <p className="claim-badge-desc">{badge.givenFor}</p>
        <button className="claim-continue-btn" onClick={onClose}>Continue Journey</button>
      </div>
    </div>
  );
}

/* ── Page ────────────────────────────────────────────────────────── */
export default function Badges({ user, token }) {
  const [activeTab, setActiveTab] = useState('all');
  const [profile, setProfile] = useState(null);
  const [claimingBadge, setClaimingBadge] = useState(null);

  useEffect(() => {
    if (!token) return;
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${API}/api/user/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setProfile(data);
      } catch(e) {
        console.error("Failed to load profile", e);
      }
    };
    fetchProfile();
  }, [token]);

  const handleClaim = async (badge) => {
    try {
      const res = await fetch(`${API}/api/user/claim_badge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ badge_id: badge.id })
      });
      if(res.ok) {
        setClaimingBadge(badge);
        setProfile(prev => ({
          ...prev,
          claimed_badges: [...(prev?.claimed_badges || []), badge.id]
        }));
      }
    } catch(e) {
      console.error(e);
    }
  };

  const totalBadges = BADGE_CATEGORIES.reduce((a, c) => a + c.badges.length, 0);

  const filtered = activeTab === 'all'
    ? BADGE_CATEGORIES
    : BADGE_CATEGORIES.filter(c => c.id === activeTab);

  return (
    <div className="badges-page">
      {/* Hero */}
      <div className="badges-hero">
        <div className="badges-hero-bg" />
        <div className="badges-hero-content">
          <div className="badges-hero-badge-orbit">
            {[
              { id: 'streak',   rarity: 'Common',    cat: 'streak' },
              { id: 'perf',     rarity: 'Epic',      cat: 'performance' },
              { id: 'vol',      rarity: 'Legendary', cat: 'volume' },
              { id: 'comp',     rarity: 'Mythic',    cat: 'competitive' },
              { id: 'battle',   rarity: 'Rare',      cat: 'battle' },
              { id: 'debug',    rarity: 'Uncommon',  cat: 'debug' }
            ].map((badge, i) => (
              <span key={i} className="orbit-icon" style={{ '--idx': i, transform: 'scale(0.6)' }}>
                <AdvancedBadgeArt badgeId={badge.id} rarity={badge.rarity} category={badge.cat} />
              </span>
            ))}
          </div>
          <div className="hero-text-block">
            <h1 className="badges-hero-title">Gallery of Achievements</h1>
            <p className="badges-hero-sub">Master the magical arts of coding and earn your legendary status.</p>
            <div className="badges-hero-stats">
              <div className="hero-stat">
                <span className="hero-stat-num">{totalBadges}</span>
                <span className="hero-stat-label">Total Badges</span>
              </div>
              <div className="hero-stat">
                <span className="hero-stat-num">{BADGE_CATEGORIES.length}</span>
                <span className="hero-stat-label">Categories</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Category filter tabs */}
      <div className="badges-tabs">
        <button
          className={`badges-tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          🌐 All
        </button>
        {BADGE_CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`badges-tab ${activeTab === cat.id ? 'active' : ''}`}
            style={activeTab === cat.id ? { '--tab-color': cat.accentColor } : {}}
            onClick={() => setActiveTab(cat.id)}
          >
            {cat.icon} {cat.title.split(' ')[0]}
          </button>
        ))}
      </div>

      {/* Categories */}
      <div className="badges-categories-list">
        {filtered.map(cat => (
          <CategorySection key={cat.id} category={cat} userProfile={profile} onClaim={handleClaim} />
        ))}
      </div>

      {claimingBadge && <ClaimBadgeModal badge={claimingBadge} onClose={() => setClaimingBadge(null)} />}
    </div>
  );
}
