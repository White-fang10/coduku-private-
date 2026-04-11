import React, { useEffect, useState, useRef } from 'react';
import './ScorePopup.css';

const HOUSE_CONFIG = {
  Gryffindor: { color: '#c8102e', glow: 'rgba(200,16,46,0.5)',  logo: '/house_logos/gryffindor.png' },
  Slytherin:  { color: '#1a7a3c', glow: 'rgba(26,122,60,0.5)',  logo: '/house_logos/slytherin.png'  },
  Ravenclaw:  { color: '#0057b8', glow: 'rgba(0,87,184,0.5)',   logo: '/house_logos/ravenclaw.png'  },
  Hufflepuff: { color: '#f0c030', glow: 'rgba(240,192,48,0.5)', logo: '/house_logos/hufflepuff.png' },
};

const MSG_MAP = {
  perfect: ['Legendary Spellcasting!',  'The Council is in awe.',         '✨'],
  great:   ['Strong Arcane Performance', 'Your magic grows stronger.',     '⚡'],
  partial: ['Partial Incantation',       'The spell needs refinement.',    '🌀'],
  wrong:   ['The Spell Fizzled...',      'Study the ancient texts again.', '💨'],
};

// Normalize any score to 0–10 (Flask returns 0–250, Judge service returns 0–10)
function normalizeScore(raw) {
  if (raw == null) return 0;
  if (raw > 10) return Math.min(10, Math.round((raw / 250) * 100) / 10);
  return raw;
}

function getMsg(score, verdict) {
  if (verdict === 'Accepted')                                          return MSG_MAP.perfect;
  if (verdict === 'Partially Correct')  return score >= 5 ? MSG_MAP.great : MSG_MAP.partial;
  if (['Wrong Answer','Runtime Error','Compilation Error','Time Limit Exceeded'].includes(verdict))
                                                                       return MSG_MAP.wrong;
  if (score >= 9.5) return MSG_MAP.perfect;
  if (score >= 7)   return MSG_MAP.great;
  if (score >= 3)   return MSG_MAP.partial;
  return MSG_MAP.wrong;
}

function Particles({ color, count = 18 }) {
  return (
    <div className="sp-particles" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <span key={i} className="sp-particle" style={{
          '--angle': `${(360 / count) * i}deg`,
          '--dist':  `${90 + Math.random() * 60}px`,
          '--delay': `${Math.random() * 0.3}s`,
          '--color': color,
          '--size':  `${6 + Math.random() * 6}px`,
        }} />
      ))}
    </div>
  );
}

function ScoreBar({ label, value, max, color, delay }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="sp-bar-row" style={{ '--delay': delay }}>
      <div className="sp-bar-label">{label}</div>
      <div className="sp-bar-track">
        <div className="sp-bar-fill" style={{ '--pct': `${pct}%`, '--color': color }} />
      </div>
      <div className="sp-bar-val">{typeof value === 'number' ? value.toFixed(1) : value}</div>
    </div>
  );
}

export default function ScorePopup({ result, user, onClose }) {
  const sub     = result?.submission || result || {};
  const bd      = sub.score_breakdown;
  const verdict = sub.verdict || 'Wrong Answer';
  const passed  = sub.passed_test_cases ?? sub.passed_tests ?? 0;
  const total   = sub.total_test_cases  ?? sub.total_tests  ?? 0;

  const rawScore    = normalizeScore(bd ? bd.visible_score : (sub.score ?? 0));
  const correctness = bd ? bd.correctness : Math.round((passed / Math.max(total, 1)) * 7 * 10) / 10;
  const timeBonus   = bd ? bd.time_bonus  : 0;
  const memBonus    = bd ? bd.memory_bonus : 0;

  const house   = HOUSE_CONFIG[user?.house] || HOUSE_CONFIG.Gryffindor;
  const houseName = user?.house || 'Gryffindor';
  const [msg, sub2, icon] = getMsg(rawScore, verdict);
  const isGood  = verdict === 'Accepted' || verdict === 'Partially Correct';
  const scoreColor = rawScore >= 9 ? '#34d399' : rawScore >= 6 ? '#fbbf24' : '#f87171';

  const [display, setDisplay] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    const start = performance.now();
    const duration = 1200;
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(eased * rawScore * 10) / 10);
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [rawScore]);

  useEffect(() => {
    const h = e => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [onClose]);

  return (
    <div className="sp-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="sp-modal" style={{ '--house-color': house.color, '--house-glow': house.glow }}>

        {isGood && <Particles color={house.color} count={20} />}

        <div className="sp-rune-bar">
          {['ᚠ','ᚢ','ᚦ','ᚨ','ᚱ','ᚲ','ᚷ','ᚹ','ᚺ','ᚾ'].map((r, i) => (
            <span key={i} className="sp-rune" style={{ '--i': i }}>{r}</span>
          ))}
        </div>

        <div className="sp-house-badge">
          <img
            src={house.logo}
            alt={houseName}
            className="sp-house-logo"
            onError={e => { e.target.style.display = 'none'; }}
          />
          <span className="sp-house-name">{houseName}</span>
        </div>

        <div className="sp-icon">{icon}</div>
        <h2 className="sp-title">{msg}</h2>
        <p className="sp-subtitle">{sub2}</p>

        <div className="sp-score-wrap">
          <div className="sp-score-ring" style={{ '--color': scoreColor, '--glow': scoreColor }}>
            <span className="sp-score-num" style={{ color: scoreColor }}>
              {display.toFixed(1)}
            </span>
            <span className="sp-score-denom">/ 10</span>
          </div>
          <div className="sp-verdict-chip" data-verdict={verdict.toLowerCase().replace(/\s+/g, '-')}>
            {verdict}
          </div>
        </div>

        <div className="sp-breakdown">
          <ScoreBar label="Correctness" value={correctness} max={7}   color="#a78bfa" delay="0.1s" />
          <ScoreBar label="⚡ Time"     value={timeBonus}   max={1.5} color="#34d399" delay="0.2s" />
          <ScoreBar label="💾 Memory"   value={memBonus}    max={1.5} color="#38bdf8" delay="0.3s" />
        </div>

        {bd && (bd.first_solve_bonus > 0 || bd.streak_bonus > 0 || bd.wrong_attempt_penalty > 0) && (
          <div className="sp-bonuses">
            {bd.first_solve_bonus > 0    && <div className="sp-bonus-chip gold">🏆 First Solver +{bd.first_solve_bonus}</div>}
            {bd.streak_bonus > 0         && <div className="sp-bonus-chip fire">🔥 Streak +{bd.streak_bonus}</div>}
            {bd.wrong_attempt_penalty > 0 && <div className="sp-bonus-chip penalty">⚠ Penalty −{bd.wrong_attempt_penalty}</div>}
            <div className="sp-leaderboard-pts">
              Leaderboard: <strong>{bd.leaderboard_points?.toFixed(1)} pts</strong>
            </div>
          </div>
        )}

        <div className="sp-tests">{passed}/{total} test cases passed</div>

        <button className="sp-close-btn" onClick={onClose}>
          <span className="sp-close-rune">ᚷ</span> Continue the Quest
        </button>

        <span className="sp-corner sp-corner-tl">✦</span>
        <span className="sp-corner sp-corner-tr">✦</span>
        <span className="sp-corner sp-corner-bl">✦</span>
        <span className="sp-corner sp-corner-br">✦</span>
      </div>
    </div>
  );
}
