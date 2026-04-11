import React, { useState, useEffect, useRef } from 'react';

export default function GoldenSnitch() {
  const [pos, setPos] = useState({ x: -100, y: 100 });
  const [rotation, setRotation] = useState(0);
  const [scale, setScale] = useState(1);
  const snitchRef = useRef(null);

  useEffect(() => {
    // Start interval to move the snitch to random spots
    const moveSnitch = () => {
      const vh = window.innerHeight;
      const vw = window.innerWidth;
      
      // Random position
      const newX = Math.random() * (vw - 50);
      const newY = Math.random() * (vh - 50);
      
      // Random rotation
      const newRot = (Math.random() - 0.5) * 120; // -60 to 60 deg
      
      // Random scale to simulate depth
      const newScale = 0.5 + Math.random() * 0.8; // 0.5 to 1.3

      setPos({ x: newX, y: newY });
      setRotation(newRot);
      setScale(newScale);
    };

    // Move initially
    setTimeout(moveSnitch, 500);

    // Randomize movement every 2-4 seconds
    const interval = setInterval(moveSnitch, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      className="golden-snitch-dynamic" 
      ref={snitchRef}
      style={{
        transform: `translate(${pos.x}px, ${pos.y}px) scale(${scale}) rotate(${rotation}deg)`,
      }}
      aria-hidden="true"
    >
      <div className="snitch-wing left" />
      <div className="snitch-wing right" />
    </div>
  );
}
