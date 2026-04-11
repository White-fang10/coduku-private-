import React, { useMemo } from 'react';
import './ComplexityGraphs.css';

// Helper to generate a realistic looking log-normal/bell curve distribution
function generateDistributionData(userValue, type, language) {
  // Number of bins
  const binCount = 30;
  
  // Base ranges depending on type
  let min, max, peak;
  if (type === 'runtime') {
    // Runtime spreads out more, exponential-like decay after peak
    min = Math.max(0, userValue - 50);
    max = userValue + 150;
    peak = userValue > 20 ? userValue - 10 : userValue + 5;
  } else {
    // Memory is tighter
    min = Math.max(10, userValue - 15);
    max = userValue + 25;
    peak = userValue - 2;
  }

  const step = (max - min) / binCount;
  let data = [];
  let totalArea = 0;
  
  for (let i = 0; i < binCount; i++) {
    const binVal = min + i * step;
    // Bell curve formula centered at 'peak'
    const variance = type === 'runtime' ? 20 : 5;
    const distance = Math.abs(binVal - peak);
    let height = Math.exp(-0.5 * Math.pow(distance / variance, 2)) * 100;
    
    // Add some noise
    height += Math.random() * 5;
    height = Math.max(1, height); // ensure minimum height
    
    data.push({
      x: binVal,
      count: height,
      isUserBin: binVal <= userValue && userValue < binVal + step
    });
    totalArea += height;
  }

  // Ensure exactly one bin is marked as user bin, just in case
  let found = false;
  let percentileAcc = 0;
  let userPercentile = 0;

  for (let i = 0; i < data.length; i++) {
    if (data[i].isUserBin && !found) {
      found = true;
      userPercentile = 100 - (percentileAcc / totalArea) * 100;
    } else {
      data[i].isUserBin = false;
    }
    percentileAcc += data[i].count;
  }
  
  if (!found) {
    // Fallback if out of bounds
    data[Math.floor(binCount / 3)].isUserBin = true;
    userPercentile = 80 + Math.random() * 15; // fake high percentile
  }

  // Normalize heights to 0-100%
  const maxCount = Math.max(...data.map(d => d.count));
  data.forEach(d => {
    d.heightPct = (d.count / maxCount) * 100;
  });

  return {
    bins: data,
    beatsPercentile: userPercentile.toFixed(2),
    min,
    max,
    step
  };
}

export default function ComplexityGraphs({ executionTimeSec, language, codeLength = 500 }) {
  // Convert sec to ms
  const runtimeMs = (executionTimeSec * 1000) || 0;
  
  // Fake memory generation: base + code length factor
  // python is around 15-20MB, java is around 40MB minimum
  let memBase = 15;
  if (language === 'java') memBase = 42;
  else if (['cpp', 'c', 'rust', 'go'].includes(language)) memBase = 5;
  else if (language === 'javascript' || language === 'python') memBase = 25;
  
  const mockMemoryMb = Number((memBase + (codeLength / 1500)).toFixed(2));

  // Determine user runtime ms to display (Leecode usually shows whole numbers or 1-2 dec)
  const displayRuntime = runtimeMs < 1 ? '< 1' : Math.round(runtimeMs);

  const runtimeDist = useMemo(() => generateDistributionData(runtimeMs === 0 ? 1 : runtimeMs, 'runtime', language), [runtimeMs, language]);
  const memoryDist = useMemo(() => generateDistributionData(mockMemoryMb, 'memory', language), [mockMemoryMb, language]);

  return (
    <div className="complexity-container">
      {/* Runtime Graph Segment */}
      <div className="complexity-card">
        <div className="complexity-header">
          <div className="complexity-title">
            <span className="complexity-icon" style={{color: '#34d399'}}>⚡</span> Runtime
          </div>
          <div className="complexity-main-val">{displayRuntime} <span className="complexity-unit">ms</span></div>
          <div className="complexity-beats" style={{color: '#34d399'}}>
            Beats {runtimeDist.beatsPercentile}%
          </div>
        </div>
        
        <div className="complexity-chart">
          {runtimeDist.bins.map((bin, i) => (
            <div 
              key={i} 
              className={`complexity-bar ${bin.isUserBin ? 'user-target' : ''}`}
              style={{ height: `${Math.max(2, bin.heightPct)}%` }}
              title={`~${Math.round(bin.x)} ms`}
            />
          ))}
        </div>
        <div className="complexity-axis">
          <span>{Math.round(runtimeDist.min)}</span>
          <span className="complexity-axis-label">ms</span>
          <span>{Math.round(runtimeDist.max)}</span>
        </div>
      </div>

      {/* Memory Graph Segment */}
      <div className="complexity-card">
        <div className="complexity-header">
          <div className="complexity-title">
            <span className="complexity-icon" style={{color: '#38bdf8'}}>💾</span> Memory
          </div>
          <div className="complexity-main-val">{mockMemoryMb} <span className="complexity-unit">MB</span></div>
          <div className="complexity-beats" style={{color: '#38bdf8'}}>
            Beats {memoryDist.beatsPercentile}%
          </div>
        </div>
        
        <div className="complexity-chart memory-chart">
          {memoryDist.bins.map((bin, i) => (
            <div 
              key={i} 
              className={`complexity-bar ${bin.isUserBin ? 'user-target' : ''}`}
              style={{ height: `${Math.max(2, bin.heightPct)}%` }}
              title={`~${bin.x.toFixed(1)} MB`}
            />
          ))}
        </div>
        <div className="complexity-axis">
          <span>{memoryDist.min.toFixed(0)}</span>
          <span className="complexity-axis-label">MB</span>
          <span>{memoryDist.max.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
}
