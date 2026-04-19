import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const label = status === 'approved' ? 'Onaylı' :
                status === 'suspicious' ? 'Şüpheli' :
                status === 'rejected' ? 'Reddedildi' : status;

  return (
    <span className={`badge badge-${status}`}>
      {status === 'suspicious' && '⚠ '}
      {label}
    </span>
  );
}
