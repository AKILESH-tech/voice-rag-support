import type { Timings } from '../types';

interface Props {
  timings: Timings;
}

export default function TelemetryBar({ timings }: Props) {
  return (
    <div className="flex gap-4 text-xs text-gray-500 bg-gray-50 border rounded px-3 py-2">
      <span>🔍 Retrieval: <strong>{timings.retrieval_latency_ms}ms</strong></span>
      <span>🤖 Generation: <strong>{timings.generation_latency_ms}ms</strong></span>
      <span>⚡ Total: <strong>{timings.total_ms}ms</strong></span>
    </div>
  );
}
