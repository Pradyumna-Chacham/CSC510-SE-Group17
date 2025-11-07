// -----------------------------------------------------------------------------
// File: client.js
// Description: API client configuration for ReqEngine frontend - handles
//              HTTP requests to the FastAPI backend with axios configuration.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  // Session Management
  createSession: (data) => apiClient.post('/session/create', data),
  updateSession: (data) => apiClient.post('/session/update', data),
  getSessionHistory: (sessionId, limit = 10) => 
    apiClient.get(`/session/${sessionId}/history`, { params: { limit } }),
  getSessions: () => apiClient.get('/sessions/'),
  deleteSession: (sessionId) => apiClient.delete(`/session/${sessionId}`),
  exportSession: (sessionId) => apiClient.get(`/session/${sessionId}/export`),

  // Use Case Extraction
  extractFromText: (data) => apiClient.post('/parse_use_case_rag/', data),
  extractFromDocument: (formData) => 
    apiClient.post('/parse_use_case_document/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Use Case Operations
  refineUseCase: (data) => apiClient.post('/use-case/refine', data),
  getSessionUseCases: (sessionId) => apiClient.get(`/session/${sessionId}/history`),

  // ❌ REMOVED: Analytics
  // getMetrics: (sessionId) => apiClient.get(`/session/${sessionId}/metrics`),
  // getConflicts: (sessionId) => apiClient.get(`/session/${sessionId}/conflicts`),

  // Query
  queryRequirements: (data) => apiClient.post('/query', data),

  // Export
  exportDOCX: (sessionId) => 
    apiClient.get(`/session/${sessionId}/export/docx`, { responseType: 'blob' }),
  exportMarkdown: (sessionId) => 
    apiClient.get(`/session/${sessionId}/export/markdown`, { responseType: 'blob' }),
  exportPlantUML: (sessionId) => apiClient.get(`/session/${sessionId}/export/plantuml`),

  // Health Check
  health: () => apiClient.get('/health'),
};

export default apiClient;