import React from 'react';

/**
 * Procedurally generates realistic, metallic SVG badges.
 * @param {string} rarity Common, Uncommon, Rare, Epic, Legendary, Mythic
 * @param {string} category streak, performance, volume, competitive, battle, debug, special, house
 * @param {string} iconName string mapped to an inner SVG path
 */
export default function MetallicBadgeSVG({ badgeId, rarity, category, size = 100 }) {
  // Define metallic gradients based on rarity
  const getGradients = () => {
    switch(rarity) {
      case 'Mythic': return {
        bg: ['#2e0c3a', '#0d021c'],
        border: ['#e2b0ff', '#8f00ff', '#e2b0ff', '#4a00e0'],
        highlight: '#ffffff',
        fx: 'url(#prism-fx)'
      };
      case 'Legendary': return {
        bg: ['#3a0c0c', '#1a0202'],
        border: ['#ffd700', '#ff8c00', '#ffd700', '#b8860b'],
        highlight: '#ffebcd',
        fx: 'none'
      };
      case 'Epic': return {
        bg: ['#1c0c3a', '#08011a'],
        border: ['#d8b4e2', '#9b59b6', '#d8b4e2', '#5b2c6f'],
        highlight: '#f4ecf7',
        fx: 'none'
      };
      case 'Rare': return {
        bg: ['#3a350c', '#171401'],
        border: ['#f9e79f', '#f1c40f', '#f9e79f', '#b7950b'],
        highlight: '#fef9e7',
        fx: 'none'
      };
      case 'Uncommon': return {
        bg: ['#0c2a3a', '#01111a'],
        border: ['#d6eaf8', '#85c1e9', '#d6eaf8', '#3498db'],
        highlight: '#ebf5fb',
        fx: 'none'
      };
      case 'Common': default: return {
        bg: ['#2c1c14', '#120803'], // Bronze/Copper
        border: ['#e59866', '#d35400', '#e59866', '#873600'],
        highlight: '#fdf2e9',
        fx: 'none'
      };
    }
  };

  const getGeometry = () => {
    switch(category) {
      case 'streak': // Hexagon
        return "M50,5 L90,25 L90,75 L50,95 L10,75 L10,25 Z";
      case 'performance': // Diamond
        return "M50,5 L95,50 L50,95 L5,50 Z";
      case 'volume': // Circle-ish polygon
        return "M50,5 A45,45 0 1,1 49.9,5 Z";
      case 'competitive': // Shield
        return "M15,10 L85,10 L85,40 C85,75 50,95 50,95 C50,95 15,75 15,40 Z";
      case 'battle': // Battle shield
        return "M50,5 L95,25 L85,85 L50,95 L15,85 L5,25 Z";
      case 'debug': // Octagon
        return "M30,10 L70,10 L90,30 L90,70 L70,90 L30,90 L10,70 L10,30 Z";
      default: // Default Crest
        return "M50,10 C70,10 90,30 85,60 C80,90 50,95 50,95 C50,95 20,90 15,60 C10,30 30,10 50,10 Z";
    }
  };

  const getInnerSymbol = () => {
    // A few generic symbols that can map decently. Using simple SVG paths.
    if(badgeId.includes('streak')) return <path d="M45,25 L65,25 L55,50 L75,50 L40,80 L45,55 L25,55 Z" fill="url(#highlight-grad)" />;
    if(badgeId.includes('perf')) return <path d="M50,20 L65,40 L55,40 L60,80 L35,50 L45,50 Z" fill="url(#highlight-grad)" />;
    if(badgeId.includes('vol')) return <g fill="url(#highlight-grad)"><path d="M30,30 L70,30 L70,70 L30,70 Z M40,40 L60,40 L60,60 L40,60 Z" /></g>;
    if(badgeId.includes('comp')) return <g><circle cx="50" cy="50" r="15" fill="none" stroke="url(#highlight-grad)" strokeWidth="6"/><path d="M50,20 L55,30 L65,30 L55,40 L60,50 L50,45 L40,50 L45,40 L35,30 L45,30 Z" fill="url(#highlight-grad)"/></g>;
    if(badgeId.includes('battle')) return <path d="M30,70 L70,30 M30,30 L70,70" stroke="url(#highlight-grad)" strokeWidth="6" strokeLinecap="round"/>;
    if(badgeId.includes('debug')) return <path d="M40,30 A10,10 0 1,1 60,30 A10,10 0 1,1 40,30 M50,40 L50,70" stroke="url(#highlight-grad)" strokeWidth="6" strokeLinecap="round" fill="none"/>;
    
    // Default Star
    return <path d="M50,25 L56,40 L72,40 L59,50 L64,65 L50,55 L36,65 L41,50 L28,40 L44,40 Z" fill="url(#highlight-grad)" />;
  };

  const colors = getGradients();
  const pathData = getGeometry();
  const idPrefix = `${badgeId}-`;

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.4))' }}>
      <defs>
        <linearGradient id={`${idPrefix}bg-grad`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colors.bg[0]} />
          <stop offset="100%" stopColor={colors.bg[1]} />
        </linearGradient>
        
        <linearGradient id={`${idPrefix}border-grad`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colors.border[0]} />
          <stop offset="30%" stopColor={colors.border[1]} />
          <stop offset="70%" stopColor={colors.border[2]} />
          <stop offset="100%" stopColor={colors.border[3]} />
        </linearGradient>

        <linearGradient id={`highlight-grad`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={colors.highlight} />
          <stop offset="100%" stopColor={colors.border[1]} />
        </linearGradient>

        <filter id="glow-fx">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Main Base */}
      <path d={pathData} fill={`url(#${idPrefix}bg-grad)`} stroke={`url(#${idPrefix}border-grad)`} strokeWidth="6" strokeLinejoin="round" />
      
      {/* Inner Bevel */}
      <path d={pathData} fill="none" stroke="#fff" strokeWidth="1" strokeOpacity="0.3" transform="scale(0.9) translate(5, 5)" />

      {/* Mythic/Legendary Accents */}
      {(rarity === 'Mythic' || rarity === 'Legendary') && (
        <path d={pathData} fill="none" stroke={`url(#${idPrefix}border-grad)`} strokeWidth="2" transform="scale(0.8) translate(12, 12)" />
      )}

      {/* Inner Symbol */}
      {getInnerSymbol()}

      {/* Mythic Sparkles */}
      {rarity === 'Mythic' && (
        <g fill="#fff">
          <circle cx="20" cy="30" r="2" filter="url(#glow-fx)"/>
          <circle cx="80" cy="25" r="1.5" filter="url(#glow-fx)"/>
          <circle cx="50" cy="85" r="2.5" filter="url(#glow-fx)"/>
        </g>
      )}
    </svg>
  );
}
