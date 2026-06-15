import { useEffect, useRef, useState } from 'react';

const RADIUS = 46;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const CATEGORIES = [
  { key: 'chat', label: 'Chat', color: '#2563eb', gradient: 'from-blue-600 to-blue-500' },
  { key: 'cowork', label: 'Cowork', color: '#7c3aed', gradient: 'from-purple-600 to-purple-500' },
  { key: 'code', label: 'Code', color: '#059669', gradient: 'from-emerald-600 to-emerald-500' },
];

export default function DonutChart({ categories = {} }) {
  const [animated, setAnimated] = useState(false);
  const ref = useRef(null);
  const total = (categories.chat || 0) + (categories.cowork || 0) + (categories.code || 0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, []);

  if (total === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3">
        <svg viewBox="0 0 120 120" className="w-28 h-28">
          <circle cx="60" cy="60" r={RADIUS} fill="none" stroke="#ebdcc5" strokeWidth="12" opacity="0.5" />
          <text x="60" y="56" textAnchor="middle" className="fill-surface-500 text-[11px] font-semibold">No</text>
          <text x="60" y="70" textAnchor="middle" className="fill-surface-500 text-[11px] font-semibold">Data</text>
        </svg>
      </div>
    );
  }

  let offset = 0;
  const segments = CATEGORIES.map(cat => {
    const value = categories[cat.key] || 0;
    const percentage = value / total;
    const dashLength = CIRCUMFERENCE * percentage;
    const dashOffset = -offset;
    offset += dashLength;
    return { ...cat, value, percentage, dashLength, dashOffset };
  });

  return (
    <div className="flex items-center gap-5">
      {/* SVG Donut */}
      <div className="relative">
        <svg viewBox="0 0 120 120" className="w-[120px] h-[120px] -rotate-90">
          {/* Background ring */}
          <circle cx="60" cy="60" r={RADIUS} fill="none" stroke="#f6f2eb" strokeWidth="14" />
          {/* Segments */}
          {segments.map((seg, i) => (
            <circle
              key={seg.key}
              cx="60"
              cy="60"
              r={RADIUS}
              fill="none"
              stroke={seg.color}
              strokeWidth="14"
              strokeDasharray={`${seg.dashLength} ${CIRCUMFERENCE - seg.dashLength}`}
              strokeDashoffset={seg.dashOffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
              style={{
                opacity: animated ? 1 : 0,
                transitionDelay: `${i * 150}ms`,
              }}
            />
          ))}
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-surface-900">{total}</span>
          <span className="text-[10px] text-surface-500 font-semibold uppercase tracking-wider">Total</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-col gap-2.5">
        {segments.map(seg => (
          <div key={seg.key} className="flex items-center gap-2.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: seg.color }} />
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-surface-700">{seg.label}</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-sm font-bold text-surface-900">{seg.value}</span>
                <span className="text-[10px] text-surface-500 font-medium">{total > 0 ? Math.round(seg.percentage * 100) : 0}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
