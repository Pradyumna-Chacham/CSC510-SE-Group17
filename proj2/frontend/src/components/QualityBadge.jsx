import React from 'react';
import { getQualityColor, getQualityLabel } from '../utils/formatters';

function QualityBadge({ score }) {
  const colorClass = getQualityColor(score);
  const label = getQualityLabel(score);

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}>
      {label} ({score}/100)
    </span>
  );
}

export default QualityBadge;