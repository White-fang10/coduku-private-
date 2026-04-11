import React from 'react';
import './MentorCharacter.css';

// ── House mentor metadata ────────────────────────────────────────────────────
const MENTOR = {
  Gryffindor: {
    name: 'McGonagall',
    fullName: 'Prof. Minerva McGonagall',
    quote: 'Think carefully. Every mistake is a lesson waiting to be unwrapped.',
    primary: '#ae0001',
    accent: '#eeba30',
    glow: 'rgba(174,0,1,0.5)',
  },
  Slytherin: {
    name: 'Snape',
    fullName: 'Prof. Severus Snape',
    quote: 'Mediocrity is a choice. I trust you will choose otherwise.',
    primary: '#1d5c38',
    accent: '#a8c0b0',
    glow: 'rgba(29,92,56,0.55)',
  },
  Ravenclaw: {
    name: 'Flitwick',
    fullName: 'Prof. Filius Flitwick',
    quote: 'Wonderful question! Curiosity is the wand of the intellect!',
    primary: '#1e3a8a',
    accent: '#cd7f32',
    glow: 'rgba(30,58,138,0.55)',
  },
  Hufflepuff: {
    name: 'Sprout',
    fullName: 'Prof. Pomona Sprout',
    quote: "You're doing wonderfully! Let's grow through this together.",
    primary: '#b8860b',
    accent: '#f5e642',
    glow: 'rgba(184,134,11,0.55)',
  },
};

// ── SVG: McGonagall (Gryffindor) ─────────────────────────────────────────────
function McGonagallSVG() {
  return (
    <svg viewBox="0 0 100 210" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="mcg-face" cx="50%" cy="40%" r="55%">
          <stop offset="0%" stopColor="#f7dfc0"/><stop offset="100%" stopColor="#e5c090"/>
        </radialGradient>
        <linearGradient id="mcg-robe" x1="0%" y1="0%" x2="60%" y2="100%">
          <stop offset="0%" stopColor="#c00003"/><stop offset="100%" stopColor="#7a0001"/>
        </linearGradient>
      </defs>
      {/* Pointed hat */}
      <path d="M50 5 L29 57 L71 57 Z" fill="#18181e" stroke="#eeba30" strokeWidth="1.5"/>
      <rect x="22" y="54" width="56" height="9" rx="4" fill="#18181e" stroke="#eeba30" strokeWidth="1"/>
      <rect x="22" y="56" width="56" height="4" rx="2" fill="#eeba30" opacity="0.85"/>
      {/* Hair — tight bun */}
      <ellipse cx="50" cy="76" rx="20" ry="13" fill="#444450"/>
      <ellipse cx="50" cy="68" rx="7" ry="5.5" fill="#555560"/>
      {/* Face */}
      <ellipse cx="50" cy="84" rx="15.5" ry="17" fill="url(#mcg-face)"/>
      {/* Spectacles */}
      <circle cx="43.5" cy="82" r="5.5" fill="none" stroke="#777" strokeWidth="1.5"/>
      <circle cx="56.5" cy="82" r="5.5" fill="none" stroke="#777" strokeWidth="1.5"/>
      <line x1="49" y1="82" x2="51" y2="82" stroke="#777" strokeWidth="1.5"/>
      <line x1="38" y1="81" x2="34" y2="82" stroke="#777" strokeWidth="1.2"/>
      <line x1="62" y1="81" x2="66" y2="82" stroke="#777" strokeWidth="1.2"/>
      {/* Eyes */}
      <ellipse cx="43.5" cy="82" rx="2.5" ry="2" fill="#2a2a38"/>
      <ellipse cx="56.5" cy="82" rx="2.5" ry="2" fill="#2a2a38"/>
      {/* Stern mouth */}
      <path d="M44 93 Q50 91 56 93" fill="none" stroke="#b07858" strokeWidth="1.6"/>
      {/* Neck */}
      <rect x="45" y="99" width="10" height="9" fill="#edd6a8"/>
      {/* Robes */}
      <path d="M28 105 C28 100 37 98 50 98 C63 98 72 100 72 105 L76 208 L24 208 Z" fill="url(#mcg-robe)"/>
      {/* Tartan lines */}
      <line x1="28" y1="128" x2="72" y2="128" stroke="#200000" strokeWidth="4" opacity="0.22"/>
      <line x1="27" y1="155" x2="73" y2="155" stroke="#200000" strokeWidth="4" opacity="0.22"/>
      <line x1="26" y1="182" x2="74" y2="182" stroke="#200000" strokeWidth="4" opacity="0.22"/>
      <line x1="40" y1="106" x2="37" y2="208" stroke="#200000" strokeWidth="4" opacity="0.22"/>
      <line x1="60" y1="106" x2="63" y2="208" stroke="#200000" strokeWidth="4" opacity="0.22"/>
      {/* Gold collar */}
      <path d="M33 106 Q50 114 67 106" fill="none" stroke="#eeba30" strokeWidth="2"/>
      {/* Arms — crossed */}
      <path d="M30 114 L10 150 L17 154 L36 122 Z" fill="#980002"/>
      <path d="M70 114 L86 148 L80 153 L64 122 Z" fill="#980002"/>
      {/* Wand */}
      <line x1="84" y1="148" x2="96" y2="130" stroke="#6b4226" strokeWidth="2.8" strokeLinecap="round"/>
      <ellipse cx="96" cy="129" rx="3" ry="3" fill="#eeba30" opacity="0.9"/>
      <circle cx="96" cy="129" r="5.5" fill="none" stroke="#eeba30" strokeWidth="1" opacity="0.4"/>
    </svg>
  );
}

// ── SVG: Snape (Slytherin) ───────────────────────────────────────────────────
function SnapeSVG() {
  return (
    <svg viewBox="0 0 100 210" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="snp-robe" x1="0%" y1="0%" x2="80%" y2="100%">
          <stop offset="0%" stopColor="#1c2820"/><stop offset="100%" stopColor="#0c1410"/>
        </linearGradient>
        <radialGradient id="snp-face" cx="50%" cy="42%" r="52%">
          <stop offset="0%" stopColor="#edece6"/><stop offset="100%" stopColor="#d4cfc4"/>
        </radialGradient>
      </defs>
      {/* Long black hair sides */}
      <path d="M29 66 L20 128 L29 128 L34 76 Z" fill="#141414"/>
      <path d="M71 66 L80 128 L71 128 L66 76 Z" fill="#141414"/>
      {/* Top hair */}
      <path d="M32 68 Q50 59 68 68 L68 77 Q50 66 32 77 Z" fill="#141414"/>
      {/* Face */}
      <ellipse cx="50" cy="84" rx="17" ry="19" fill="url(#snp-face)"/>
      {/* Raised eyebrows — one higher */}
      <path d="M38 75 Q42 72 46 75" fill="none" stroke="#1c1c1c" strokeWidth="1.8"/>
      <path d="M54 73 Q58 70 62 73" fill="none" stroke="#1c1c1c" strokeWidth="1.8"/>
      {/* Cold piercing eyes */}
      <ellipse cx="42" cy="80" rx="3.5" ry="2.5" fill="#162214"/>
      <ellipse cx="58" cy="80" rx="3.5" ry="2.5" fill="#162214"/>
      <circle cx="43" cy="79.5" r="1" fill="#fff" opacity="0.5"/>
      <circle cx="59" cy="79.5" r="1" fill="#fff" opacity="0.5"/>
      {/* Thin hook nose */}
      <path d="M50 85 L48 94 L53 96" fill="none" stroke="#b09878" strokeWidth="1.8"/>
      {/* Thin compressed mouth */}
      <line x1="44" y1="99" x2="56" y2="99" stroke="#907060" strokeWidth="1.5"/>
      {/* Neck */}
      <rect x="45" y="101" width="10" height="9" fill="#dedad4"/>
      {/* Dark voluminous robes */}
      <path d="M18 108 C18 103 32 100 50 100 C68 100 82 103 82 108 L88 208 L12 208 Z" fill="url(#snp-robe)"/>
      {/* Green button row */}
      {[120,142,164,186,207].map((y, i) => (
        <circle key={i} cx="50" cy={y} r="2.2" fill="#2a6040" opacity="0.85"/>
      ))}
      {/* Green accent edge */}
      <path d="M18 108 L12 208" stroke="#1d5c38" strokeWidth="2" opacity="0.5"/>
      <path d="M82 108 L88 208" stroke="#1d5c38" strokeWidth="2" opacity="0.5"/>
      {/* Cape/collar */}
      <path d="M20 109 Q50 121 80 109 Q80 123 50 128 Q20 123 20 109 Z" fill="#0c1410"/>
      {/* Arms */}
      <path d="M22 120 L5 162 L12 166 L28 130 Z" fill="#1c2820"/>
      <path d="M78 120 L90 156 L84 160 L72 130 Z" fill="#1c2820"/>
      {/* Silvery wand */}
      <line x1="88" y1="156" x2="97" y2="140" stroke="#333" strokeWidth="2.5" strokeLinecap="round"/>
      <circle cx="97" cy="139" r="3" fill="#a8c0b0" opacity="0.9"/>
      <circle cx="97" cy="139" r="5.5" fill="none" stroke="#a8c0b0" strokeWidth="1" opacity="0.35"/>
    </svg>
  );
}

// ── SVG: Flitwick (Ravenclaw) ────────────────────────────────────────────────
function FlitwickSVG() {
  return (
    <svg viewBox="0 0 100 210" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="flt-robe" x1="0%" y1="0%" x2="70%" y2="100%">
          <stop offset="0%" stopColor="#274db8"/><stop offset="100%" stopColor="#152d80"/>
        </linearGradient>
        <radialGradient id="flt-face" cx="50%" cy="46%" r="52%">
          <stop offset="0%" stopColor="#f5d898"/><stop offset="100%" stopColor="#e2b870"/>
        </radialGradient>
      </defs>
      {/* Pointed hat with bronze star */}
      <path d="M50 10 L31 55 L69 55 Z" fill="#152d80" stroke="#cd7f32" strokeWidth="1.5"/>
      <rect x="23" y="52" width="54" height="9" rx="4" fill="#152d80" stroke="#cd7f32" strokeWidth="1"/>
      <rect x="23" y="54" width="54" height="4" rx="2" fill="#cd7f32" opacity="0.9"/>
      <text x="50" y="43" textAnchor="middle" fontSize="11" fill="#cd7f32">★</text>
      {/* White wispy hair */}
      <path d="M31 70 Q50 62 69 70" fill="none" stroke="#e8e8f2" strokeWidth="5" strokeLinecap="round"/>
      {/* Round jolly face */}
      <ellipse cx="50" cy="86" rx="20" ry="19" fill="url(#flt-face)"/>
      {/* Big round excited eyes */}
      <ellipse cx="42" cy="82" rx="4.5" ry="4.5" fill="#fff"/>
      <ellipse cx="58" cy="82" rx="4.5" ry="4.5" fill="#fff"/>
      <ellipse cx="42" cy="83" rx="2.8" ry="3" fill="#274db8"/>
      <ellipse cx="58" cy="83" rx="2.8" ry="3" fill="#274db8"/>
      <circle cx="43" cy="81.5" r="1.1" fill="#fff"/>
      <circle cx="59" cy="81.5" r="1.1" fill="#fff"/>
      {/* Bushy eyebrows */}
      <path d="M37 75 Q42 71 47 75" fill="none" stroke="#888" strokeWidth="2.5" strokeLinecap="round"/>
      <path d="M53 75 Q58 71 63 75" fill="none" stroke="#888" strokeWidth="2.5" strokeLinecap="round"/>
      {/* Big grin */}
      <path d="M39 95 Q50 106 61 95" fill="none" stroke="#c08050" strokeWidth="2.5"/>
      {/* Rosy cheeks */}
      <ellipse cx="37" cy="91" rx="5" ry="3" fill="#f0a0a0" opacity="0.35"/>
      <ellipse cx="63" cy="91" rx="5" ry="3" fill="#f0a0a0" opacity="0.35"/>
      {/* Neck */}
      <rect x="45" y="103" width="10" height="9" fill="#e8c888"/>
      {/* Wide robe */}
      <path d="M24 110 C24 105 36 103 50 103 C64 103 76 105 76 110 L72 208 L28 208 Z" fill="url(#flt-robe)"/>
      {/* Bronze buttons */}
      {[122,145,168,191,208].map((y, i) => (
        <circle key={i} cx="50" cy={y} r="2.5" fill="#cd7f32"/>
      ))}
      {/* Bronze collar */}
      <path d="M28 111 Q50 120 72 111" fill="none" stroke="#cd7f32" strokeWidth="2.2"/>
      {/* Enthusiastic arms raised */}
      <path d="M26 118 L7 88 L13 84 L32 114 Z" fill="#274db8"/>
      <path d="M74 118 L93 88 L87 84 L68 114 Z" fill="#274db8"/>
      {/* Wand with sparkle burst */}
      <line x1="9" y1="87" x2="2" y2="73" stroke="#6b4226" strokeWidth="3" strokeLinecap="round"/>
      <circle cx="2" cy="72" r="4.5" fill="#cd7f32" opacity="0.95"/>
      <circle cx="2" cy="72" r="8" fill="none" stroke="#cd7f32" strokeWidth="1" opacity="0.4"/>
      <line x1="2" y1="63" x2="2" y2="68" stroke="#cd7f32" strokeWidth="1.5"/>
      <line x1="-6" y1="72" x2="-1" y2="72" stroke="#cd7f32" strokeWidth="1.5"/>
      <line x1="10" y1="72" x2="5" y2="72" stroke="#cd7f32" strokeWidth="1.5"/>
      <line x1="-4" y1="66" x2="0" y2="70" stroke="#cd7f32" strokeWidth="1.5"/>
      <line x1="8" y1="66" x2="4" y2="70" stroke="#cd7f32" strokeWidth="1.5"/>
    </svg>
  );
}

// ── SVG: Sprout (Hufflepuff) ─────────────────────────────────────────────────
function SproutSVG() {
  return (
    <svg viewBox="0 0 100 210" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="spr-robe" x1="0%" y1="0%" x2="70%" y2="100%">
          <stop offset="0%" stopColor="#6b8c3a"/><stop offset="100%" stopColor="#4a6228"/>
        </linearGradient>
        <radialGradient id="spr-face" cx="50%" cy="46%" r="55%">
          <stop offset="0%" stopColor="#f0d088"/><stop offset="100%" stopColor="#d4a855"/>
        </radialGradient>
      </defs>
      {/* Wide floppy brown hat */}
      <ellipse cx="50" cy="57" rx="38" ry="8" fill="#5a4020"/>
      <path d="M50 18 L36 54 L64 54 Z" fill="#4a3018"/>
      {/* Flowers on hat */}
      <circle cx="38" cy="52" r="4.5" fill="#f5e642" opacity="0.9"/>
      <circle cx="56" cy="50" r="3.5" fill="#ff9090" opacity="0.9"/>
      <circle cx="67" cy="53" r="4" fill="#f5e642" opacity="0.85"/>
      <circle cx="75" cy="56" r="3" fill="#90c890" opacity="0.85"/>
      <circle cx="25" cy="55" r="3" fill="#ff9090" opacity="0.8"/>
      {/* Grey hair showing under hat */}
      <path d="M28 67 Q50 60 72 67 Q72 79 50 80 Q28 79 28 67 Z" fill="#c0b8b2"/>
      {/* Round warm face */}
      <ellipse cx="50" cy="88" rx="21" ry="20" fill="url(#spr-face)"/>
      {/* Warm crinkled happy eyes */}
      <path d="M39 82 Q43 79 47 82" fill="none" stroke="#5a4020" strokeWidth="2.8" strokeLinecap="round"/>
      <path d="M53 82 Q57 79 61 82" fill="none" stroke="#5a4020" strokeWidth="2.8" strokeLinecap="round"/>
      {/* Rosy cheeks */}
      <ellipse cx="37" cy="92" rx="6" ry="4" fill="#e08868" opacity="0.3"/>
      <ellipse cx="63" cy="92" rx="6" ry="4" fill="#e08868" opacity="0.3"/>
      {/* Big warm smile */}
      <path d="M40 97 Q50 108 60 97" fill="none" stroke="#a06040" strokeWidth="2.8"/>
      {/* Neck */}
      <rect x="44" y="106" width="12" height="9" fill="#d4a855"/>
      {/* Wide earthy robes */}
      <path d="M16 113 C16 107 32 105 50 105 C68 105 84 107 84 113 L88 208 L12 208 Z" fill="url(#spr-robe)"/>
      {/* Apron patch */}
      <rect x="34" y="122" width="32" height="52" rx="5" fill="#8b6c38" opacity="0.38"/>
      {/* Yellow collar */}
      <path d="M20 114 Q50 124 80 114" fill="none" stroke="#f5e642" strokeWidth="2.5"/>
      {/* Arms open welcomingly */}
      <path d="M18 122 L4 165 L11 168 L26 132 Z" fill="#5a7830"/>
      <path d="M82 122 L94 158 L88 162 L74 132 Z" fill="#5a7830"/>
      {/* Potted plant in left hand */}
      <rect x="-4" y="162" width="15" height="13" rx="3" fill="#8b5e3c"/>
      <path d="M3.5 162 Q3.5 148 11 142" fill="none" stroke="#4a7028" strokeWidth="3.5" strokeLinecap="round"/>
      <ellipse cx="13" cy="140" rx="7" ry="4.5" fill="#5aa038"/>
      <path d="M4 152 Q10 145 17 152" fill="none" stroke="#6ab048" strokeWidth="2.5" strokeLinecap="round"/>
      {/* Wand */}
      <line x1="92" y1="158" x2="100" y2="143" stroke="#6b4226" strokeWidth="3" strokeLinecap="round"/>
      <ellipse cx="100" cy="141" rx="5" ry="3" fill="#4a8020" transform="rotate(-25 100 141)"/>
    </svg>
  );
}

const CHAR_SVG = {
  Gryffindor: <McGonagallSVG />,
  Slytherin:  <SnapeSVG />,
  Ravenclaw:  <FlitwickSVG />,
  Hufflepuff: <SproutSVG />,
};

// ── Main Component ────────────────────────────────────────────────────────────
export default function MentorCharacter({ house, mentorOpen, onToggle }) {
  const mentor  = MENTOR[house]   || MENTOR.Gryffindor;
  const charSvg = CHAR_SVG[house] || CHAR_SVG.Gryffindor;

  return (
    <div
      className={`mentor-character ${mentorOpen ? 'panel-open' : ''}`}
      style={{
        '--mentor-primary': mentor.primary,
        '--mentor-accent':  mentor.accent,
        '--mentor-glow':    mentor.glow,
      }}
      onClick={onToggle}
      title={`Chat with ${mentor.fullName}`}
      role="button"
      aria-label={mentorOpen ? `Close ${mentor.fullName}` : `Open ${mentor.fullName}`}
    >
      {/* Speech bubble — visible on hover when panel closed */}
      <div className="mentor-bubble">{mentor.quote}</div>

      {/* Character figure */}
      <div className="mentor-char-figure">{charSvg}</div>

      {/* Name tag */}
      <div className="mentor-nametag">{mentor.name}</div>
    </div>
  );
}
