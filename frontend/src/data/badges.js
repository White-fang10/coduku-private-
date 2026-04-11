/* ── Badge Data ─────────────────────────────────────────────────── */
export const BADGE_CATEGORIES = [
  {
    id: 'streak',
    icon: '🔥',
    title: 'Streak-Based Badges',
    subtitle: 'Consistency Magic',
    seriesName: '🪄 Daily Discipline Series',
    accentColor: '#ff6b35',
    gradientFrom: 'rgba(255,107,53,0.15)',
    badges: [
      { id: 'streak_3',   name: 'First Spark',           icon: '✨', rarity: 'Common',    color: '#fbbf24', givenFor: '3-day coding streak',     design: 'Small glowing wand tip with faint golden sparks on a dark background', image: '/clean-badges/streak-based-badges/first-spark.png' },
      { id: 'streak_7',   name: 'Steady Wand',           icon: '🪄', rarity: 'Common',    color: '#a78bfa', givenFor: '7-day streak',             design: 'Wand with a stable glowing aura forming a circle', image: '/clean-badges/streak-based-badges/study-wand.png' },
      { id: 'streak_14',  name: 'Spell Weaver',          icon: '🌀', rarity: 'Uncommon',  color: '#38bdf8', givenFor: '14-day streak',            design: 'Intertwined magical threads forming a rune-like symbol', image: '/clean-badges/streak-based-badges/spell-weaver.png' },
      { id: 'streak_30',  name: 'Arcane Habit',          icon: '⭕', rarity: 'Rare',      color: '#818cf8', givenFor: '30-day streak',            design: 'Circular magic sigil with rotating glyphs', image: '/clean-badges/streak-based-badges/arcane-habit.png' },
      { id: 'streak_60',  name: 'Time-Turner Adept',     icon: '⏳', rarity: 'Epic',      color: '#d4af37', givenFor: '60-day streak',            design: 'Golden rotating hourglass with magical particles', image: '/clean-badges/streak-based-badges/time-turner-adept.png' },
      { id: 'streak_100', name: 'Master of Persistence', icon: '🦅', rarity: 'Legendary', color: '#ef4444', givenFor: '100-day streak',           design: 'Flaming phoenix outline made of code symbols', image: '/clean-badges/streak-based-badges/master-of-persistence.png' },
    ]
  },
  {
    id: 'performance',
    icon: '⚡',
    title: 'Performance-Based Badges',
    subtitle: 'Speed + Complexity',
    seriesName: '🧠 Efficiency Magic Series',
    accentColor: '#3b82f6',
    gradientFrom: 'rgba(59,130,246,0.15)',
    badges: [
      { id: 'perf_quickdraw',    name: 'Quick-Draw Wizard',    icon: '⚡', rarity: 'Common',    color: '#fbbf24', givenFor: 'Solving within top time threshold',                design: 'Wand casting a sharp lightning bolt', image: '/clean-badges/performance-based-badges/quick-draw-wizard.png' },
      { id: 'perf_lightning',    name: 'Lightning Caster',     icon: '🌩', rarity: 'Uncommon',  color: '#38bdf8', givenFor: 'Top 10% execution speed',                          design: 'Blue lightning enclosed in a glowing crest', image: '/clean-badges/performance-based-badges/lightning-caster.png' },
      { id: 'perf_complexity',   name: 'Complexity Sage',      icon: '🌌', rarity: 'Rare',      color: '#8b5cf6', givenFor: 'Optimal Big-O detected',                           design: 'Spiral galaxy pattern representing algorithm efficiency', image: '/clean-badges/performance-based-badges/complexity-sage.png' },
      { id: 'perf_alchemist',    name: 'Efficiency Alchemist', icon: '⚗️', rarity: 'Epic',      color: '#f59e0b', givenFor: 'Improving solution performance multiple times',     design: 'Potion flask transforming from red → gold', image: '/clean-badges/performance-based-badges/efficiency-alchemist.png' },
      { id: 'perf_perfection',   name: 'Arcane Perfection',    icon: '💎', rarity: 'Legendary', color: '#d4af37', givenFor: 'Best speed + best complexity combo',               design: 'Radiant staff with crystal core emitting energy rings', image: '/clean-badges/performance-based-badges/arcane-perfection.png' },
    ]
  },
  {
    id: 'volume',
    icon: '📚',
    title: 'Problem-Solved Badges',
    subtitle: 'Volume',
    seriesName: '📜 Spell Mastery Series',
    accentColor: '#10b981',
    gradientFrom: 'rgba(16,185,129,0.15)',
    badges: [
      { id: 'vol_10',   name: 'First Incantation',  icon: '📜', rarity: 'Common',    color: '#10b981', givenFor: '10 problems solved',   design: 'Scroll with a single glowing rune', image: '/clean-badges/problem-solved-badges-volume/first-incantation.png' },
      { id: 'vol_25',   name: 'Apprentice Caster',  icon: '📖', rarity: 'Common',    color: '#34d399', givenFor: '25 problems',           design: 'Open spellbook with faint light', image: '/clean-badges/problem-solved-badges-volume/apperentice-caster.png' },
      { id: 'vol_50',   name: 'Rune Collector',     icon: '🔮', rarity: 'Uncommon',  color: '#6ee7b7', givenFor: '50 problems',           design: 'Collection of floating runes orbiting', image: '/clean-badges/problem-solved-badges-volume/rune-collecter.png' },
      { id: 'vol_100',  name: 'Arcane Scholar',     icon: '📚', rarity: 'Rare',      color: '#a78bfa', givenFor: '100 problems',          design: 'Thick enchanted book with glowing edges', image: '/clean-badges/problem-solved-badges-volume/archane-scholar.png' },
      { id: 'vol_250',  name: 'Order of Coders',    icon: '⚔️', rarity: 'Epic',      color: '#8b5cf6', givenFor: '250 problems',          design: 'Crest with crossed wands and magical shield', image: '/clean-badges/problem-solved-badges-volume/order-of-codes.png' },
      { id: 'vol_500',  name: 'Grand Magus',        icon: '👑', rarity: 'Legendary', color: '#d4af37', givenFor: '500 problems',          design: 'Crown infused with magical energy', image: '/clean-badges/problem-solved-badges-volume/grand-magus.png' },
      { id: 'vol_1000', name: 'Eternal Archmage',   icon: '🌟', rarity: 'Mythic',    color: '#f0abfc', givenFor: '1000 problems',         design: 'Floating throne of light with arcane symbols', image: '/clean-badges/problem-solved-badges-volume/eternal-archmage.png' },
    ]
  },
  {
    id: 'competitive',
    icon: '🏆',
    title: 'Competitive Badges',
    subtitle: 'Leaderboard',
    seriesName: '🏅 House Glory Series',
    accentColor: '#d4af37',
    gradientFrom: 'rgba(212,175,55,0.15)',
    badges: [
      { id: 'comp_champion',   name: 'House Champion',      icon: '🛡️', rarity: 'Epic',      color: '#d4af37', givenFor: 'Rank #1 in house',             design: 'Shield with house colors and glowing border', image: '/clean-badges/competitive-badges-leaderboard/house-champion.png' },
      { id: 'comp_elite',      name: 'Arcane Elite',        icon: '⭐', rarity: 'Legendary', color: '#f0abfc', givenFor: 'Top 3 overall leaderboard',    design: 'Three floating stars forming a triangle', image: '/clean-badges/competitive-badges-leaderboard/arcane-elite.png' },
      { id: 'comp_rising',     name: 'Rising Conjurer',     icon: '🌠', rarity: 'Uncommon',  color: '#38bdf8', givenFor: 'Weekly top performer',          design: 'Star shooting upward with trail', image: '/clean-badges/competitive-badges-leaderboard/rising-concurer.png' },
      { id: 'comp_unchallenged', name: 'Unchallenged Wizard', icon: '🌀', rarity: 'Mythic', color: '#c084fc', givenFor: 'Long leaderboard streak',       design: 'Crown surrounded by rotating magical rings', image: '/clean-badges/competitive-badges-leaderboard/unchallenged-wizard.png' },
    ]
  },
  {
    id: 'battle',
    icon: '⚔️',
    title: 'Battle Mode Badges',
    subtitle: 'Duel Arena + Relay',
    seriesName: '🎮 Duel Arena Series',
    accentColor: '#ef4444',
    gradientFrom: 'rgba(239,68,68,0.15)',
    badges: [
      { id: 'battle_initiate',   name: 'Duel Initiate',      icon: '⚔️', rarity: 'Common',    color: '#38bdf8', givenFor: 'First battle win',        design: 'Two crossed glowing wands', image: '/clean-badges/battle-mode-badges/duel-initiate.png' },
      { id: 'battle_duelist',    name: 'Spell Duelist',       icon: '✨', rarity: 'Uncommon',  color: '#a78bfa', givenFor: '5 wins',                   design: 'Wand clash emitting sparks', image: '/clean-badges/battle-mode-badges/spell-duelist.png' },
      { id: 'battle_conqueror',  name: 'Arena Conqueror',     icon: '🏟', rarity: 'Rare',      color: '#ef4444', givenFor: '20 wins',                  design: 'Arena circle with magical barrier', image: '/clean-badges/battle-mode-badges/arena-conqurer.png' },
      { id: 'battle_unstoppable',name: 'Unstoppable Caster',  icon: '🔥', rarity: 'Epic',      color: '#ff6b35', givenFor: 'Win streak',               design: 'Flame trail behind a wand slash', image: '/clean-badges/battle-mode-badges/unster-caster.png' },
      { id: 'relay_team',        name: 'Team Conjurer',       icon: '🤝', rarity: 'Common',    color: '#10b981', givenFor: 'First relay completion',    design: 'Chain of glowing runes connected', series: '🤝 Relay Mode Series' },
      { id: 'relay_seamless',    name: 'Seamless Sorcery',    icon: '🎗', rarity: 'Rare',      color: '#38bdf8', givenFor: 'Perfect relay execution',   design: 'Smooth flowing magical ribbon', series: '🤝 Relay Mode Series' },
      { id: 'relay_chain',       name: 'Chain Master',        icon: '💠', rarity: 'Epic',      color: '#8b5cf6', givenFor: 'MVP in relay',             design: 'Linked rings with central glowing gem', series: '🤝 Relay Mode Series' },
    ]
  },
  {
    id: 'debug',
    icon: '🤖',
    title: 'Debugging & AI Badges',
    subtitle: 'Mind Magic',
    seriesName: '🧩 Mind Magic Series',
    accentColor: '#8b5cf6',
    gradientFrom: 'rgba(139,92,246,0.15)',
    badges: [
      { id: 'debug_hunter',  name: 'Bug Hunter',          icon: '🕸', rarity: 'Common',    color: '#10b981', givenFor: 'First debugging success',   design: 'Small creature trapped in magical net', image: '/clean-badges/debugging-and-ai/bug-hunter.png' },
      { id: 'debug_healer',  name: 'Code Healer',         icon: '💊', rarity: 'Uncommon',  color: '#34d399', givenFor: 'Fix 10 bugs',               design: 'Wand repairing broken code fragments', image: '/clean-badges/debugging-and-ai/corenen-comente.png' },
      { id: 'debug_hybrid',  name: 'Hybrid Thinker',      icon: '🧠', rarity: 'Rare',      color: '#818cf8', givenFor: 'AI-assisted solve',          design: 'Half-human, half-glowing AI brain symbol', image: '/clean-badges/debugging-and-ai/hybrid-thinker.png' },
      { id: 'debug_dark',    name: 'Dark Pattern Breaker', icon: '💥', rarity: 'Epic',     color: '#8b5cf6', givenFor: 'Solve complex bug',          design: 'Cracked dark orb releasing light', image: '/clean-badges/debugging-and-ai/darked-barker.png' },
    ]
  },
  {
    id: 'special',
    icon: '🧪',
    title: 'Special / Rare Badges',
    subtitle: 'Unique Challenges',
    seriesName: '✨ Legendary Collection',
    accentColor: '#f0abfc',
    gradientFrom: 'rgba(240,171,252,0.15)',
    badges: [
      { id: 'spec_veil',     name: 'Veil Walker',      icon: '👻', rarity: 'Epic',      color: '#c084fc', givenFor: 'Solve without hints',                      design: 'Transparent cloak silhouette', image: '/clean-badges/special-rare-badges/veil-walker.png' },
      { id: 'spec_phoenix',  name: 'Phoenix Return',   icon: '🦜', rarity: 'Rare',      color: '#f59e0b', givenFor: 'Return after inactivity',                  design: 'Phoenix rising from ashes', image: '/clean-badges/special-rare-badges/phoenix-return.png' },
      { id: 'spec_night',    name: 'Night Marauder',   icon: '🌙', rarity: 'Uncommon',  color: '#818cf8', givenFor: 'Late-night coding streak',                 design: 'Crescent moon with glowing code', image: '/clean-badges/special-rare-badges/night-marauder.png' },
      { id: 'spec_forbidden',name: 'Forbidden Solver', icon: '🌑', rarity: 'Legendary', color: '#6d28d9', givenFor: 'Solve hardest difficulty problems',        design: 'Dark forest with glowing path', image: '/clean-badges/special-rare-badges/forbidden-solver.png' },
      { id: 'spec_edge',     name: 'Edge Case Slayer', icon: '💠', rarity: 'Epic',      color: '#38bdf8', givenFor: 'Solve tricky edge-case heavy problems',    design: 'Sharp crystal shattering into pieces', image: '/clean-badges/special-rare-badges/edge-case-slayer.png' },
    ]
  },
  {
    id: 'house',
    icon: '🏰',
    title: 'House Contribution Badges',
    subtitle: 'House Pride',
    seriesName: '🏛 Allegiance Series',
    accentColor: '#d4af37',
    gradientFrom: 'rgba(212,175,55,0.12)',
    badges: [
      { id: 'house_loyal',   name: 'Loyal Mage',        icon: '🏠', rarity: 'Common',    color: '#10b981', givenFor: 'First contribution to house points',   design: 'Small glowing house emblem', image: '/clean-badges/house-contribution-badges/loyal-mage.png' },
      { id: 'house_pillar',  name: 'House Pillar',      icon: '🏛', rarity: 'Rare',      color: '#d4af37', givenFor: 'High contribution',                    design: 'Strong pillar infused with magic', image: '/clean-badges/house-contribution-badges/house-pillar.png' },
      { id: 'house_chosen',  name: 'The Chosen Caster', icon: '🌟', rarity: 'Legendary', color: '#f0abfc', givenFor: 'Carry team in event',                  design: 'Bright aura figure standing alone', image: '/clean-badges/house-contribution-badges/the-chosen-caster.png' },
    ]
  },
];

export const RARITY_META = {
  Common:    { color: '#10b981', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.3)',  stars: 1 },
  Uncommon:  { color: '#38bdf8', bg: 'rgba(56,189,248,0.12)', border: 'rgba(56,189,248,0.3)',  stars: 2 },
  Rare:      { color: '#a78bfa', bg: 'rgba(167,139,250,0.12)', border: 'rgba(167,139,250,0.3)', stars: 3 },
  Epic:      { color: '#8b5cf6', bg: 'rgba(139,92,246,0.12)', border: 'rgba(139,92,246,0.3)',  stars: 4 },
  Legendary: { color: '#d4af37', bg: 'rgba(212,175,55,0.12)', border: 'rgba(212,175,55,0.3)',  stars: 5 },
  Mythic:    { color: '#f0abfc', bg: 'rgba(240,171,252,0.12)', border: 'rgba(240,171,252,0.3)', stars: 5 },
};
