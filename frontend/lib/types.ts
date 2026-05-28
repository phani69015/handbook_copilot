export interface College {
  college_name: string;
  college_code: string;
  total_chunks: number;
  is_indexed: boolean;
  has_openai_key: boolean;
  created_at: string;
}

export interface Citation {
  section: string;
  page: number;
  relevance_score: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  chunks_used: number;
  confidence: number;
  college_name: string;
}

export interface RegisterRequest {
  college_name: string;
  invite_code: string;
  openai_api_key: string;
}

export interface RegisterResponse {
  college_name: string;
  college_code: string;
  has_openai_key: boolean;
  message: string;
}

export interface IngestResponse {
  status: string;
  chunks_created: number;
  pages_processed: number;
  source_file: string;
  college_code: string;
}

export interface HealthResponse {
  status: string;
  qdrant_connected: boolean;
  ollama_available: boolean;
  llm_provider: string;
  embedding_provider: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  chunks_used?: number;
  confidence?: number;
}
