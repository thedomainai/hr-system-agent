import type {
  CompanyCreateRequest,
  CompanyResponse,
  WorkflowResponse,
  WorkflowStartRequest,
  PolicyOutputResponse,
  HITLRequestResponse,
  HITLDecisionRequest,
  HITLDecisionResponse,
  HealthResponse,
} from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ========================================
// HTTP Helpers
// ========================================

async function fetchJson<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      error.detail || `Request failed: ${response.statusText}`
    );
  }

  return response.json();
}

async function get<T>(url: string): Promise<T> {
  return fetchJson<T>(url, { method: 'GET' });
}

async function post<T>(url: string, data?: unknown): Promise<T> {
  return fetchJson<T>(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

async function del<T>(url: string): Promise<T> {
  return fetchJson<T>(url, { method: 'DELETE' });
}

// ========================================
// Error Class
// ========================================

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ========================================
// API Client
// ========================================

export const apiClient = {
  // Health
  health: {
    check: () => get<HealthResponse>('/health'),
  },

  // Companies
  companies: {
    create: (data: CompanyCreateRequest) =>
      post<CompanyResponse>('/companies', data),
    get: (companyId: string) =>
      get<CompanyResponse>(`/companies/${companyId}`),
    delete: (companyId: string) =>
      del<{ status: string; company_id: string }>(`/companies/${companyId}`),
  },

  // Workflows
  workflows: {
    start: (data: WorkflowStartRequest) =>
      post<WorkflowResponse>('/policies/workflows', data),
    getStatus: (workflowId: string) =>
      get<WorkflowResponse>(`/policies/workflows/${workflowId}`),
    getOutput: (workflowId: string) =>
      get<PolicyOutputResponse>(`/policies/workflows/${workflowId}/output`),
    retryStep: (workflowId: string, stepId: string) =>
      post<WorkflowResponse>(
        `/policies/workflows/${workflowId}/steps/${stepId}/retry`
      ),
  },

  // Reviews (HITL)
  reviews: {
    getPending: (companyId: string) =>
      get<HITLRequestResponse[]>(`/reviews/pending/${companyId}`),
    get: (requestId: string) =>
      get<HITLRequestResponse>(`/reviews/${requestId}`),
    submitDecision: (requestId: string, decision: HITLDecisionRequest) =>
      post<HITLDecisionResponse>(`/reviews/${requestId}/decision`, decision),
    cancel: (requestId: string) =>
      post<{ status: string; request_id: string }>(
        `/reviews/${requestId}/cancel`
      ),
  },
};

export default apiClient;
