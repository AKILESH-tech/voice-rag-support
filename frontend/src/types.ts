export interface Document {
  id: string
  filename: string
  page_count?: number
  chunk_count?: number
  status: 'pending' | 'indexing' | 'indexed' | 'failed'
  created_at: string
}

export interface Citation {
  page_number: number
  chunk_text: string
  score: number
  rank: number
}

export interface Timings {
  retrieval_latency_ms: number
  generation_latency_ms: number
  stt_latency_ms: number
  total_latency_ms?: number
}

export interface QueryResult {
  query_id: string
  answer: string
  confidence: number
  citations: Citation[]
  timings: Timings
}

