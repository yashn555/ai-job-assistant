import React from 'react';
import { Clock, Sparkles, Eye, CheckCircle, AlertTriangle, FastForward } from 'lucide-react';

export default function StatusBadge({ status }) {
  const normStatus = (status || 'DRAFT').toUpperCase();

  switch (normStatus) {
    case 'DRAFT':
    case 'READY':
      return (
        <span className="badge badge-draft">
          <Clock size={12} /> Ready to Generate
        </span>
      );
    case 'GENERATED':
      return (
        <span className="badge badge-generated">
          <Sparkles size={12} /> Email Generated
        </span>
      );
    case 'REVIEWED':
      return (
        <span className="badge badge-generated">
          <Eye size={12} /> Reviewed
        </span>
      );
    case 'SENT':
      return (
        <span className="badge badge-sent">
          <CheckCircle size={12} /> Sent
        </span>
      );
    case 'FAILED':
      return (
        <span className="badge badge-failed">
          <AlertTriangle size={12} /> Failed
        </span>
      );
    case 'SKIPPED':
      return (
        <span className="badge badge-skipped">
          <FastForward size={12} /> Skipped
        </span>
      );
    default:
      return (
        <span className="badge badge-draft">
          {normStatus}
        </span>
      );
  }
}
