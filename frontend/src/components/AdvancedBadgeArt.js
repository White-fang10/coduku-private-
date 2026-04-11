import React from 'react';
import { 
  Wand2, IterationCw, Hourglass, Flame, Zap, ZapOff, Sparkles, 
  FlaskConical, Gem, Scroll, Book, BookOpen, Shield, Crown, 
  Orbit, Star, Swords, ShieldAlert, Link, Brain, Bug, Ghost, 
  Moon, TreePine, Hexagon, Tentacle, Rocket, Code, Award, Target, Beaker,
  ShieldHalf, Sword, Crosshair, Feather
} from 'lucide-react';
import './AdvancedBadgeArt.css';

export default function AdvancedBadgeArt({ badgeId, rarity, category }) {
  // Common effect helpers
  const Particles = ({ count, color, type }) => (
    <div className={`badge-art-particles ${type}`}>
      {[...Array(count)].map((_, i) => (
        <div key={i} className="particle" style={{ '--i': i, background: color }} />
      ))}
    </div>
  );

  const GlowRing = ({ color, duration }) => (
    <div className="badge-ring" style={{ borderColor: color, animationDuration: duration }}></div>
  );

  const getArtContent = () => {
    switch (badgeId) {
      // 1. STRREAK BADGES
      case 'streak_3': return (
        <div className="art-layer">
          <Wand2 className="icon-base top-glow" size={32} color="#fbbf24" />
          <Particles count={5} color="#fbbf24" type="spark-float" />
        </div>
      );
      case 'streak_7': return (
        <div className="art-layer">
          <GlowRing color="rgba(167,139,250,0.8)" duration="4s" />
          <Wand2 className="icon-base pulse" size={36} color="#a78bfa" />
        </div>
      );
      case 'streak_14': return (
        <div className="art-layer rotate-slow">
          <IterationCw className="icon-base" size={40} color="#38bdf8" />
          <Orbit className="icon-overlay spin-reverse" size={48} color="rgba(56,189,248,0.5)" />
        </div>
      );
      case 'streak_30': return (
        <div className="art-layer">
          <div className="sigil-circle spin" style={{borderColor: '#818cf8'}}></div>
          <Hexagon className="icon-base spin-reverse" size={36} color="#818cf8" />
        </div>
      );
      case 'streak_60': return (
        <div className="art-layer">
          <Hourglass className="icon-base spin-stop" size={40} color="#d4af37" />
          <Particles count={8} color="#d4af37" type="sand-fall" />
        </div>
      );
      case 'streak_100': return (
        <div className="art-layer">
          <Flame className="icon-base phoenix-flame" size={50} color="#ef4444" />
          <Code className="icon-overlay code-pulse" size={24} color="#fca5a5" />
        </div>
      );

      // 2. PERFORMANCE BADGES
      case 'perf_quickdraw': return (
        <div className="art-layer">
          <Wand2 className="icon-base tilt" size={32} color="#fbbf24" />
          <Zap className="icon-overlay flash" size={40} color="#fef08a" style={{ transform: 'translate(10px, -10px)' }}/>
        </div>
      );
      case 'perf_lightning': return (
        <div className="art-layer crest-bg shield-clip">
          <Zap className="icon-base zap-pulse" size={44} color="#60a5fa" />
        </div>
      );
      case 'perf_complexity': return (
        <div className="art-layer">
          <div className="galaxy-spiral spin"></div>
          <Sparkles className="icon-base" size={32} color="#c084fc" />
        </div>
      );
      case 'perf_alchemist': return (
        <div className="art-layer">
          <FlaskConical className="icon-base fill-anim" size={40} color="#f59e0b" />
          <Particles count={6} color="#fbbf24" type="bubble-up" />
        </div>
      );
      case 'perf_perfection': return (
        <div className="art-layer">
          <Target className="icon-base pulse-ring" size={44} color="#d4af37" />
          <Gem className="icon-overlay float" size={20} color="#ffffff" />
        </div>
      );

      // 3. VOLUME BADGES
      case 'vol_10': return (
        <div className="art-layer">
          <Scroll className="icon-base" size={38} color="#10b981" />
          <div className="rune-glow" style={{background: '#34d399'}}></div>
        </div>
      );
      case 'vol_25': return (
        <div className="art-layer">
          <BookOpen className="icon-base glow-pulse" size={40} color="#34d399" />
        </div>
      );
      case 'vol_50': return (
        <div className="art-layer">
          <Orbit className="icon-base spin" size={50} color="#6ee7b7" />
          <Gem className="icon-overlay float" size={16} color="#6ee7b7" />
        </div>
      );
      case 'vol_100': return (
        <div className="art-layer">
          <Book className="icon-base thick-glow" size={46} color="#a78bfa" />
        </div>
      );
      case 'vol_250': return (
        <div className="art-layer">
          <Shield className="icon-base" size={48} color="#8b5cf6" />
          <Swords className="icon-overlay float" size={24} color="#ddd" />
        </div>
      );
      case 'vol_500': return (
        <div className="art-layer">
          <Crown className="icon-base corona-glow" size={50} color="#d4af37" />
        </div>
      );
      case 'vol_1000': return (
        <div className="art-layer float-heavy">
          <div className="throne-bg"></div>
          <Sparkles className="icon-base pulse" size={40} color="#f0abfc" />
        </div>
      );

      // 4. COMPETITIVE BADGES
      case 'comp_champion': return (
        <div className="art-layer">
          <ShieldHalf className="icon-base house-shield filter-glow" size={50} color="#d4af37" />
        </div>
      );
      case 'comp_elite': return (
        <div className="art-layer triangle-float">
          <Star className="icon-overlay s1" size={20} color="#f0abfc" />
          <Star className="icon-overlay s2" size={20} color="#f0abfc" />
          <Star className="icon-overlay s3" size={20} color="#f0abfc" />
        </div>
      );
      case 'comp_rising': return (
        <div className="art-layer">
          <Star className="icon-base shoot-up" size={32} color="#38bdf8" />
          <div className="star-trail"></div>
        </div>
      );
      case 'comp_unchallenged': return (
        <div className="art-layer">
          <Orbit className="icon-overlay spin" size={55} color="#c084fc" />
          <Crown className="icon-base float" size={32} color="#d4af37" />
        </div>
      );

      // 5. BATTLE BADGES
      case 'battle_initiate': return (
        <div className="art-layer">
          <Sword className="icon-overlay cross-left" size={36} color="#38bdf8" />
          <Sword className="icon-overlay cross-right" size={36} color="#38bdf8" />
        </div>
      );
      case 'battle_duelist': return (
        <div className="art-layer clash-shake">
          <Swords className="icon-base" size={42} color="#a78bfa" />
          <Particles count={4} color="#e9d5ff" type="spark-burst" />
        </div>
      );
      case 'battle_conqueror': return (
        <div className="art-layer">
          <Target className="icon-base arena-shield" size={50} color="#ef4444" />
        </div>
      );
      case 'battle_unstoppable': return (
        <div className="art-layer wand-slash">
          <Wand2 className="icon-base slash-anim" size={40} color="#ff6b35" />
          <Flame className="icon-overlay trail-flame" size={24} color="#ffed4a" />
        </div>
      );

      // RELAY BADGES
      case 'relay_team': return (
        <div className="art-layer chain-link">
          <Link className="icon-base pulse" size={40} color="#10b981" />
        </div>
      );
      case 'relay_seamless': return (
        <div className="art-layer">
          <div className="magic-ribbon flow-anim"></div>
        </div>
      );
      case 'relay_chain': return (
        <div className="art-layer">
          <Orbit className="icon-base spin" size={46} color="#8b5cf6" />
          <Gem className="icon-overlay core-pulse" size={20} color="#c084fc" />
        </div>
      );

      // 6. DEBUGGING
      case 'debug_hunter': return (
        <div className="art-layer">
          <Bug className="icon-base trap-shake" size={32} color="#10b981" />
          <div className="magic-net"></div>
        </div>
      );
      case 'debug_healer': return (
        <div className="art-layer">
          <Wand2 className="icon-base code-heal" size={32} color="#34d399" />
          <Code className="icon-overlay broken-code" size={20} color="#fff" />
        </div>
      );
      case 'debug_hybrid': return (
        <div className="art-layer split-brain">
          <Brain className="icon-base" size={42} color="#818cf8" />
          <div className="ai-glow-half"></div>
        </div>
      );
      case 'debug_dark': return (
        <div className="art-layer">
          <Orbit className="icon-base dark-orb crack" size={40} color="#4c1d95" />
          <Sparkles className="icon-overlay light-leak" size={24} color="#ddd" />
        </div>
      );

      // 7. SPECIAL BADGES
      case 'spec_veil': return (
        <div className="art-layer">
          <Ghost className="icon-base veil-float" size={40} color="#c084fc" />
        </div>
      );
      case 'spec_phoenix': return (
        <div className="art-layer">
          <Feather className="icon-base ash-rise" size={40} color="#f59e0b" />
          <Particles count={6} color="#d97706" type="ash-float" />
        </div>
      );
      case 'spec_night': return (
        <div className="art-layer">
          <Moon className="icon-base night-glow" size={38} color="#818cf8" />
          <Code className="icon-overlay z-float" size={16} color="#fff" />
        </div>
      );
      case 'spec_forbidden': return (
        <div className="art-layer">
          <TreePine className="icon-base dark-forest" size={44} color="#4c1d95" />
          <div className="glow-path"></div>
        </div>
      );
      case 'spec_edge': return (
        <div className="art-layer">
          <Hexagon className="icon-base shatter-cryst" size={40} color="#38bdf8" />
        </div>
      );

      // 8. HOUSE BADGES
      case 'house_loyal': return (
        <div className="art-layer">
          <ShieldAlert className="icon-base house-pulse" size={36} color="#10b981" />
        </div>
      );
      case 'house_pillar': return (
        <div className="art-layer">
          <div className="magic-pillar"></div>
          <Sparkles className="icon-overlay top-glow" size={20} color="#d4af37" />
        </div>
      );
      case 'house_chosen': return (
        <div className="art-layer">
          <Orbit className="icon-base aura-burst" size={50} color="#f0abfc" />
          <Star className="icon-overlay core-star" size={24} color="#fff" />
        </div>
      );

      // Default fallback
      default: return (
        <div className="art-layer">
          <Award className="icon-base glow" size={40} color="#fff" />
        </div>
      );
    }
  };

  return (
    <div className={`adv-badge-art ${rarity?.toLowerCase()}`}>
      {/* Background magical container effect */}
      <div className="adv-badge-bg"></div>
      
      {/* Dynamic Content */}
      <div className="adv-badge-inner">
        {getArtContent()}
      </div>
    </div>
  );
}
