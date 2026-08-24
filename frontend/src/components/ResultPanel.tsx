import { useState } from 'react';
import type { QueryResult } from '../types';

interface Props {
  result: QueryResult;
}

export default function ResultPanel({ result }: Props) {
  const [citationsOpen, setCitationsOpen] = useState(false);
  const confidencePct = Math.round(result.confidence * 100);
  const confidenceColor = confidencePct >= 70 ? 'bg-green-100 text-green-800' : confidencePct >= 40 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${confidenceColor}`}>
          {confidencePct}% confident
        </span>
      </div>
      <p className="text-gray-800 whitespace-pre-wrap">{result.answer}</p>
      {result.citations.length > 0 && (
        <div>
          <button
            onClick={() => setCitationsOpen(!citationsOpen)}
            className="text-sm text-blue-600 hover:underline"
          >
            {citationsOpen ? '▲ Hide' : '▼ Show'} {result.citations.length} source{result.citations.length !== 1 ? 's' : ''}
          </button>
          {citationsOpen && (
            <div className="mt-2 space-y-2">
              {result.citations.map((c, i) => (
                <div key={i} className="border-l-4 border-blue-300 pl-3 py-1 bg-blue-50 rounded">
                  <div className="text-xs text-gray-500 mb-1">
                    Page {c.page_number} · Rank {c.rank} · Score {c.score.toFixed(3)}
                  </div>
                  <p className="text-sm text-gray-700">{c.chunk_text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
