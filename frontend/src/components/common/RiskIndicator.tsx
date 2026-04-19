import React from 'react';

interface RiskIndicatorProps {
  level: string;
}

export default function RiskIndicator({ level }: RiskIndicatorProps) {
  const label = level === 'low' ? 'Düşük' :
                level === 'medium' ? 'Orta' :
                level === 'high' ? 'Yüksek' :
                level === 'critical' ? 'Kritik' : level;

  return (
    <span className={`badge badge-${level}`}>
      {level === 'critical' && '🔴 '}
      {level === 'high' && '🟠 '}
      {level === 'medium' && '🟡 '}
      {level === 'low' && '🟢 '}
      {label}
    </span>
  );
}
