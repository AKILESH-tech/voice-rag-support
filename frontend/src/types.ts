export interface Document {
  id: string;
  filename: string;
  page_count: number | null;
  chunk_count: number | null;
  status: 'pending' | 'indexed' | 'failed';
  created_at: string;
}

export interface Citation {
  page_number: number;
  chunk_text: string;
  score: number;
  rank: number;
}

export interface Timings {
  retrieval_latency_ms: number;
  generation_latency_ms: number;
  total_ms: number;
}

export interface QueryResult {
  query_id: string;
  answer: string;
  confidence: number;
  citations: Citation[];
  timings: Timings;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  result?: QueryResult;
  timestamp: Date;
}
