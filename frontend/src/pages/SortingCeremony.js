import React, { useState, useEffect, useRef, useCallback } from 'react';
import './SortingCeremony.css';

// ── Import character PNGs ──────────────────────────────────────────────────
import char1  from '../assets/characters/char1.png';
import char2  from '../assets/characters/char2.png';
import char3  from '../assets/characters/char3.png';
import char4  from '../assets/characters/char4.png';
import char5  from '../assets/characters/char5.png';
import char6  from '../assets/characters/char6.png';
import char7  from '../assets/characters/char7.png';
import char8  from '../assets/characters/char8.png';
import char9  from '../assets/characters/char9.png';
import char10 from '../assets/characters/char10.png';
import char11 from '../assets/characters/char11.png';
import char12 from '../assets/characters/char12.png';
import char13 from '../assets/characters/char13.png';
import char14 from '../assets/characters/char14.png';
import char15 from '../assets/characters/char15.png';
import sortingHat from '../assets/hat/sorting-hat.png';

// ── Character data ─────────────────────────────────────────────────────────
const CHARACTERS = [
  { id: 1,  name: 'Char 1',  src: char1,  color: '#c84b31' },
  { id: 2,  name: 'Char 2',  src: char2,  color: '#4a90d9' },
  { id: 3,  name: 'Char 3',  src: char3,  color: '#e8a800' },
  { id: 4,  name: 'Char 4',  src: char4,  color: '#2ecc71' },
  { id: 5,  name: 'Char 5',  src: char5,  color: '#9b59b6' },
  { id: 6,  name: 'Char 6',  src: char6,  color: '#e74c3c' },
  { id: 7,  name: 'Char 7',  src: char7,  color: '#27ae60' },
  { id: 8,  name: 'Char 8',  src: char8,  color: '#f39c12' },
  { id: 9,  name: 'Char 9',  src: char9,  color: '#8e44ad' },
  { id: 10, name: 'Char 10', src: char10, color: '#16a085' },
  { id: 11, name: 'Char 11', src: char11, color: '#2980b9' },
  { id: 12, name: 'Char 12', src: char12, color: '#e67e22' },
  { id: 13, name: 'Char 13', src: char13, color: '#1abc9c' },
  { id: 14, name: 'Char 14', src: char14, color: '#d35400' },
  { id: 15, name: 'Char 15', src: char15, color: '#8e44ad' },
];

// ── House data ─────────────────────────────────────────────────────────────
const HOUSES = [
  {
    name: 'Gryffindor',
    color: '#ae0001', accent: '#d4af37',
    logo: '/house_logos/gryffindor.png',
    trait: 'Brave & Bold',
    quote: 'Courage in the face of the unknown.',
    effect: 'flame',        // red flame burst
  },
  {
    name: 'Slytherin',
    color: '#1a472a', accent: '#aaaaaa',
    logo: '/house_logos/slytherin.png',
    trait: 'Cunning & Ambitious',
    quote: 'Ambition carves the path to greatness.',
    effect: 'smoke',        // green smoke swirl
  },
  {
    name: 'Ravenclaw',
    color: '#222f5b', accent: '#7fa7c9',
    logo: '/house_logos/ravenclaw.png',
    trait: 'Wise & Creative',
    quote: 'Wit beyond measure is our greatest treasure.',
    effect: 'lightning',    // blue lightning flash
  },
  {
    name: 'Hufflepuff',
    color: '#726000', accent: '#f3c623',
    logo: '/house_logos/hufflepuff.png',
    trait: 'Loyal & Hardworking',
    quote: 'True loyalty is the bravest magic of all.',
    effect: 'sparkle',      // yellow glowing particles
  },
];

function getShuffledBag() {
  const bag = [...HOUSES];
  for (let i = bag.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [bag[i], bag[j]] = [bag[j], bag[i]];
  }
  return bag;
}

function pickHouse(charId) {
  try {
    let bag = JSON.parse(localStorage.getItem('ch_sorting_bag')) || [];
    if (!Array.isArray(bag) || bag.length === 0) {
      bag = getShuffledBag().map(h => h.name);
    }
    const houseName = bag.pop();
    localStorage.setItem('ch_sorting_bag', JSON.stringify(bag));
    return HOUSES.find(h => h.name === houseName) || HOUSES[0];
  } catch (e) {
    return HOUSES[Math.floor(Math.random() * HOUSES.length)];
  }
}

// ── Sparkle particles for selection bg ────────────────────────────────────
function StarField() {
  const stars = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 0.5,
    delay: Math.random() * 5,
    dur: Math.random() * 3 + 3,
  }));
  return (
    <div className="star-field" aria-hidden="true">
      {stars.map(s => (
        <div key={s.id} className="star" style={{
          left: `${s.x}%`, top: `${s.y}%`,
          width: s.size, height: s.size,
          animationDelay: `${s.delay}s`,
          animationDuration: `${s.dur}s`,
        }} />
      ))}
    </div>
  );
}

// ── Floating dust particles ────────────────────────────────────────────────
function DustParticles({ count = 20, color = '#d4af37' }) {
  const pts = Array.from({ length: count }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: 80 + Math.random() * 20,
    size: Math.random() * 4 + 2,
    delay: Math.random() * 3,
    dur: Math.random() * 4 + 4,
  }));
  return (
    <div className="dust-particles" aria-hidden="true">
      {pts.map(p => (
        <div key={p.id} className="dust-pt" style={{
          left: `${p.x}%`, top: `${p.y}%`,
          width: p.size, height: p.size,
          background: color,
          animationDelay: `${p.delay}s`,
          animationDuration: `${p.dur}s`,
        }} />
      ))}
    </div>
  );
}

// ── Spark burst on character select ───────────────────────────────────────
function SparkBurst({ color }) {
  const sparks = Array.from({ length: 12 }, (_, i) => ({
    id: i, angle: (i / 12) * 360,
    dist: 60 + Math.random() * 40,
    delay: Math.random() * 0.2,
  }));
  return (
    <div className="spark-burst" aria-hidden="true">
      {sparks.map(s => (
        <div key={s.id} className="spark" style={{
          '--angle': `${s.angle}deg`,
          '--dist': `${s.dist}px`,
          background: color,
          animationDelay: `${s.delay}s`,
        }} />
      ))}
    </div>
  );
}

// ── Confetti system ────────────────────────────────────────────────────────
function Confetti({ color, accent }) {
  const pieces = Array.from({ length: 35 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    delay: Math.random() * 2,
    dur: Math.random() * 2.5 + 2,
    size: Math.random() * 10 + 5,
    rotation: Math.random() * 720,
    color: i % 2 === 0 ? accent : color,
    shape: i % 3 === 0 ? 'circle' : 'square',
  }));
  return (
    <div className="confetti-container" aria-hidden="true">
      {pieces.map(p => (
        <div key={p.id} className="confetti-piece" style={{
          left: `${p.x}%`,
          width: p.size, height: p.size,
          background: p.color,
          borderRadius: p.shape === 'circle' ? '50%' : '2px',
          animationDelay: `${p.delay}s`,
          animationDuration: `${p.dur}s`,
          '--rotation': `${p.rotation}deg`,
        }} />
      ))}
    </div>
  );
}

// ── House effect overlay ───────────────────────────────────────────────────
function HouseEffect({ effect, accent }) {
  if (effect === 'flame') {
    const flames = Array.from({ length: 18 }, (_, i) => ({ id: i, delay: i * 0.08 }));
    return (
      <div className="house-effect flame-effect" aria-hidden="true">
        {flames.map(f => (
          <div key={f.id} className="flame-particle" style={{ animationDelay: `${f.delay}s` }} />
        ))}
      </div>
    );
  }
  if (effect === 'smoke') {
    const puffs = Array.from({ length: 14 }, (_, i) => ({ id: i, delay: i * 0.1 }));
    return (
      <div className="house-effect smoke-effect" aria-hidden="true">
        {puffs.map(p => (
          <div key={p.id} className="smoke-puff" style={{ animationDelay: `${p.delay}s` }} />
        ))}
      </div>
    );
  }
  if (effect === 'lightning') {
    return (
      <div className="house-effect lightning-effect" aria-hidden="true">
        <div className="lightning-bolt l1" />
        <div className="lightning-bolt l2" />
        <div className="lightning-bolt l3" />
        <div className="lightning-flash" />
      </div>
    );
  }
  if (effect === 'sparkle') {
    const pts = Array.from({ length: 20 }, (_, i) => ({ id: i, delay: i * 0.07 }));
    return (
      <div className="house-effect sparkle-effect" aria-hidden="true">
        {pts.map(p => (
          <div key={p.id} className="sparkle-pt"
            style={{ animationDelay: `${p.delay}s`, '--accent': accent }} />
        ))}
      </div>
    );
  }
  return null;
}

// ── Main component ─────────────────────────────────────────────────────────
export default function SortingCeremony({ onComplete }) {
  // scene: 'selection' | 'summoning' | 'hatEntry' | 'thinking' | 'reveal' | 'result'
  const [scene, setScene]                 = useState('selection');
  const [selected, setSelected]           = useState(null);
  const [house, setHouse]                 = useState(null);
  const [hatShake, setHatShake]           = useState(false);
  const [glowIntensity, setGlowIntensity] = useState(1);
  const [thinkTick, setThinkTick]         = useState(0);
  const [showFlash, setShowFlash]         = useState(false);
  const [resultVisible, setResultVisible] = useState(false);
  const [cameraShake, setCameraShake]     = useState(false);

  const timeouts = useRef([]);
  const intervals = useRef([]);
  const t = useCallback((fn, ms) => {
    const id = setTimeout(fn, ms);
    timeouts.current.push(id);
    return id;
  }, []);
  const iv = useCallback((fn, ms) => {
    const id = setInterval(fn, ms);
    intervals.current.push(id);
    return id;
  }, []);

  useEffect(() => () => {
    timeouts.current.forEach(clearTimeout);
    intervals.current.forEach(clearInterval);
  }, []);

  // Step through scenes after selection
  const handleSelect = useCallback((char) => {
    if (scene !== 'selection') return;
    setSelected(char);
    setHouse(pickHouse(char.id));

    // Scene: summoning (character floats to center)
    t(() => setScene('summoning'), 600);
    // Scene: hat entry
    t(() => setScene('hatEntry'), 2400);
    // Scene: thinking phase
    t(() => {
      setScene('thinking');
      setHatShake(true);

      // Pulse glow intensity
      let tick = 0;
      const glowIv = iv(() => {
        tick++;
        setGlowIntensity(0.5 + Math.abs(Math.sin(tick * 0.4)) * 1.5);
        setThinkTick(tick);
      }, 180);
      intervals.current.push(glowIv);

      // End thinking → flash → reveal
      t(() => {
        intervals.current.forEach(clearInterval);
        setHatShake(false);
        setShowFlash(true);
        t(() => {
          setShowFlash(false);
          setCameraShake(true);
          setScene('reveal');
          t(() => setCameraShake(false), 700);
          t(() => {
            setResultVisible(true);
          }, 300);
        }, 400);
      }, 2200);
    }, 4000);

  }, [scene, t, iv]);

  return (
    <div className={`ceremony-root ${scene} ${cameraShake ? 'shake' : ''}`}>
      {/* Starfield always in bg */}
      <StarField />

      {/* Flash overlay */}
      {showFlash && <div className="ceremony-flash" aria-hidden="true" />}

      {/* ── SELECTION ── */}
      {scene === 'selection' && (
        <SelectionScene characters={CHARACTERS} onSelect={handleSelect} />
      )}

      {/* ── SUMMONING ── */}
      {scene === 'summoning' && selected && (
        <SummoningScene character={selected} />
      )}

      {/* ── HAT ENTRY ── */}
      {scene === 'hatEntry' && selected && (
        <HatEntryScene character={selected} />
      )}

      {/* ── THINKING ── */}
      {scene === 'thinking' && selected && (
        <ThinkingScene
          character={selected}
          hatShake={hatShake}
          glowIntensity={glowIntensity}
          tick={thinkTick}
        />
      )}

      {/* ── REVEAL ── */}
      {(scene === 'reveal') && selected && house && (
        <RevealScene
          character={selected}
          house={house}
          visible={resultVisible}
          onComplete={onComplete}
        />
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// SCENE 1 — CHARACTER SELECTION
// ════════════════════════════════════════════════════════════════
function SelectionScene({ characters, onSelect }) {
  const [hasSelected, setHasSelected] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  const handleClick = (char) => {
    if (hasSelected) return;
    setHasSelected(true);
    setSelectedId(char.id);
    setTimeout(() => onSelect(char), 700);
  };

  return (
    <div className="scene-selection">
      <DustParticles count={18} color="#a78bfa" />
      <div className="selection-header">
        <p className="selection-eyebrow">✦ The Sorting Begins ✦</p>
        <h1 className="selection-title">Choose Your Spirit</h1>
        <p className="selection-subtitle">Select the character that calls to your soul</p>
      </div>

      <div className="char-grid">
        {characters.map((char, i) => (
          <CharCard
            key={char.id}
            char={char}
            index={i}
            isSelected={selectedId === char.id}
            isDimmed={hasSelected && selectedId !== char.id}
            onClick={() => handleClick(char)}
          />
        ))}
      </div>
    </div>
  );
}

// ── Character Card ─────────────────────────────────────────────────────────
function CharCard({ char, index, isSelected, isDimmed, onClick }) {
  return (
    <div
      className={`char-card
        ${isSelected ? 'selected' : ''}
        ${isDimmed   ? 'dimmed'   : ''}
      `}
      style={{
        '--card-color': char.color,
        '--float-delay': `${(index * 0.15) % 2}s`,
        '--float-dur':   `${2.4 + (index % 4) * 0.25}s`,
        '--appear-delay': `${index * 0.06}s`,
      }}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Select ${char.name}`}
      onKeyDown={e => e.key === 'Enter' && onClick()}
    >
      <div className="card-glow" aria-hidden="true" />
      {isSelected && <SparkBurst color={char.color} />}
      <div className="card-img-wrap">
        <img src={char.src} alt={char.name} className="card-img" draggable={false} />
      </div>
      <span className="card-label">{char.name}</span>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// SCENE 2 — SUMMONING
// ════════════════════════════════════════════════════════════════
function SummoningScene({ character }) {
  return (
    <div className="scene-summoning">
      {/* Circular rune beneath */}
      <div className="rune-circle" aria-hidden="true">
        <div className="rune-ring r1" />
        <div className="rune-ring r2" />
        <div className="rune-ring r3" />
        <div className="rune-glyph" aria-hidden="true">✦ ✦ ✦ ✦ ✦</div>
      </div>

      {/* Character floating up */}
      <div className="summon-char-wrap" style={{ '--char-color': character.color }}>
        <div className="summon-aura" aria-hidden="true" />
        <img src={character.src} alt={character.name} className="summon-char-img" draggable={false} />
        <SparkBurst color={character.color} />
      </div>

      <p className="summon-text">The magic stirs...</p>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// SCENE 3 — HAT ENTRY
// ════════════════════════════════════════════════════════════════
function HatEntryScene({ character }) {
  return (
    <div className="scene-hat-entry">
      <DustParticles count={16} color="#d4af37" />

      {/* Character stays centered */}
      <div className="hat-entry-char" style={{ '--char-color': character.color }}>
        <img src={character.src} alt={character.name} className="hat-entry-char-img" draggable={false} />
      </div>

      {/* Hat drops from top */}
      <div className="hat-drop-wrap">
        <div className="hat-golden-aura" aria-hidden="true" />
        <img src={sortingHat} alt="Sorting Hat" className="hat-img hat-drop-anim" draggable={false} />
      </div>

      <p className="hat-entry-text">The Sorting Hat arrives...</p>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// SCENE 4 — THINKING
// ════════════════════════════════════════════════════════════════
function ThinkingScene({ character, hatShake, glowIntensity, tick }) {
  const pulsing = tick % 2 === 0;
  return (
    <div className="scene-thinking">
      <DustParticles count={12} color="#d4af37" />

      {/* Character */}
      <div className="thinking-char" style={{ '--char-color': character.color }}>
        <img src={character.src} alt={character.name} className="thinking-char-img" draggable={false} />
      </div>

      {/* Hat thinking */}
      <div className={`hat-think-wrap ${hatShake ? 'shake' : ''}`}>
        <div
          className="hat-think-glow"
          aria-hidden="true"
          style={{ opacity: glowIntensity * 0.4, transform: `scale(${0.9 + glowIntensity * 0.1})` }}
        />
        <img
          src={sortingHat}
          alt="Sorting Hat"
          className="hat-think-img"
          style={{ filter: `drop-shadow(0 0 ${20 + glowIntensity * 15}px rgba(212,175,55,${glowIntensity * 0.6}))` }}
          draggable={false}
        />
      </div>

      <p className="thinking-text" style={{ opacity: pulsing ? 1 : 0.5 }}>
        Hmm... Let me think...
      </p>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// SCENE 5–7 — REVEAL + FINAL RESULT
// ════════════════════════════════════════════════════════════════
function RevealScene({ character, house, visible, onComplete }) {
  return (
    <div
      className={`scene-reveal ${visible ? 'visible' : ''}`}
      style={{ '--house-color': house.color, '--house-accent': house.accent }}
    >
      {/* House-specific effect */}
      <HouseEffect effect={house.effect} accent={house.accent} />
      {visible && <Confetti color={house.color} accent={house.accent} />}

      {/* Big house emblem backdrop */}
      <div className="reveal-backdrop" aria-hidden="true">
        <img src={house.logo} alt={house.name} className="reveal-backdrop-logo" />
      </div>

      {/* Radial bg glow */}
      <div className="reveal-bg-glow" aria-hidden="true" />

      {/* Character tinted with house color */}
      <div className="reveal-char-wrap" style={{ '--char-color': house.accent }}>
        <div className="reveal-char-aura" aria-hidden="true" />
        <img
          src={character.src}
          alt={character.name}
          className="reveal-char-img"
          style={{ filter: `drop-shadow(0 0 30px ${house.accent}) saturate(1.4)` }}
          draggable={false}
        />
      </div>

      {/* House logo badge */}
      <div className="reveal-crest-wrap">
        <img src={house.logo} alt={house.name} className="reveal-crest-logo" />
      </div>

      {/* Text reveal */}
      <div className="reveal-text">
        <p className="reveal-label">YOU BELONG TO</p>
        <h2 className="reveal-house-name" style={{ color: house.accent }}>
          {house.name}
        </h2>
        <p className="reveal-trait" style={{ color: house.accent }}>{house.trait}</p>
        <p className="reveal-quote">"{house.quote}"</p>
      </div>

      {/* CTA */}
      <button
        id="enter-coduku-btn"
        className="reveal-cta"
        style={{
          borderColor: house.accent,
          color: house.accent,
          boxShadow: `0 0 30px ${house.accent}55`,
        }}
        onClick={() => onComplete({ house: house.name, character: character })}
      >
        Enter Coduku ✦
      </button>
    </div>
  );
}
