import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import QualityBadge from './QualityBadge';

function UseCaseCard({ useCase, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();

  const qualityScore = useCase.quality_score || 75;

  return (
    <div className="bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-900 flex-1">
          {useCase.title}
        </h3>
        <QualityBadge score={qualityScore} />
      </div>

      {/* Stakeholders */}
      <div className="mb-4">
        <span className="text-sm text-gray-500">Stakeholders: </span>
        <span className="text-sm text-gray-700">
          {useCase.stakeholders?.join(', ') || 'N/A'}
        </span>
      </div>

      {/* Main Flow Preview */}
      <div className="mb-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-primary hover:underline"
        >
          {expanded ? '▼ Hide Details' : '▶ Show Details'}
        </button>

        {expanded && (
          <div className="mt-4 space-y-4">
            {/* Preconditions */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Preconditions:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {useCase.preconditions?.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>

            {/* Main Flows */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Main Flows:</h4>
              {/* Support both new `main_flows` and legacy `main_flow` */}
              {(() => {
                const flows = Array.isArray(useCase.main_flows)
                  ? useCase.main_flows
                  : Array.isArray(useCase.main_flow)
                  ? [useCase.main_flow]
                  : [];
                return flows.length > 0 ? (
                <div className="space-y-2">
                  {flows.map((flow, fi) => (
                    <div key={fi} className="text-sm text-gray-600">
                      {Array.isArray(flow) ? (
                        <ol className="list-decimal list-inside">
                          {flow.map((step, si) => (
                            <li key={si}>{step}</li>
                          ))}
                        </ol>
                      ) : typeof flow === 'object' && flow !== null && Array.isArray(flow.steps) ? (
                        <ol className="list-decimal list-inside">
                          {flow.steps.map((step, si) => (
                            <li key={si}>{step}</li>
                          ))}
                        </ol>
                      ) : (
                        <div>• {String(flow)}</div>
                      )}
                    </div>
                  ))}
                </div>
                ) : null;
              })()}
            </div>

            {/* Sub Flows */}
            {Array.isArray(useCase.sub_flows) && useCase.sub_flows.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Sub Flows:</h4>
                <div className="space-y-3">
                  {useCase.sub_flows.map((sub, si) => (
                    <div key={si} className="text-sm text-gray-600">
                      {typeof sub?.title === 'string' && (
                        <div className="font-medium text-gray-700">{sub.title}</div>
                      )}
                      {Array.isArray(sub?.steps) ? (
                        <ol className="list-decimal list-inside">
                          {sub.steps.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ol>
                      ) : Array.isArray(sub) ? (
                        <ol className="list-decimal list-inside">
                          {sub.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ol>
                      ) : Array.isArray(useCase.sub_flows) ? null : null}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Alternate Flows */}
            {Array.isArray(useCase.alternate_flows) && useCase.alternate_flows.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Alternate Flows:</h4>
                <ul className="list-disc list-inside text-sm text-gray-600">
                  {useCase.alternate_flows.map((alt, i) => (
                    <li key={i}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Outcomes */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Outcomes:</h4>
              <ul className="list-disc list-inside text-sm text-gray-600">
                {useCase.outcomes?.map((o, i) => (
                  <li key={i}>{o}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => navigate(`/use-case/${useCase.id}`)}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-indigo-700 transition text-sm"
        >
          View Details
        </button>
        <button
          onClick={() => navigate(`/use-case/${useCase.id}/refine`)}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition text-sm"
        >
          Refine
        </button>
        {onDelete && (
          <button
            onClick={() => onDelete(useCase.id)}
            className="px-4 py-2 bg-red-100 text-red-600 rounded hover:bg-red-200 transition text-sm"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

export default UseCaseCard;