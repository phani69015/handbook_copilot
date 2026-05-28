import {
  College,
  HealthResponse,
  IngestResponse,
  QueryResponse,
  RegisterRequest,
  RegisterResponse,
} from './types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }

  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchAPI<HealthResponse>('/health');
}

export async function listColleges(): Promise<{ colleges: College[]; total: number }> {
  return fetchAPI('/colleges');
}

export async function getCollege(code: string): Promise<College> {
  return fetchAPI<College>(`/colleges/${code}`);
}

export async function registerCollege(data: RegisterRequest): Promise<RegisterResponse> {
  return fetchAPI<RegisterResponse>('/colleges/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function ingestHandbook(
  collegeCode: string,
  file: File,
  forceReindex: boolean = false
): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('force_reindex', String(forceReindex));

  const res = await fetch(`${BACKEND_URL}/colleges/${collegeCode}/ingest`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Ingestion failed: ${res.status}`);
  }

  return res.json();
}

export async function queryHandbook(
  collegeCode: string,
  question: string
): Promise<QueryResponse> {
  return fetchAPI<QueryResponse>(`/colleges/${collegeCode}/query`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}
