import axios from 'axios'
import type { Document, QueryResult } from '../types'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ACCESS_TOKEN_KEY = 'voice_rag_access_token'

const api = axios.create({ baseURL: BASE })

export interface UsageResponse {
  used: number
  limit: number
  remaining: number
}

export interface AuthMeResponse {
  uid: string
  email: string
  provider: string
}

export interface SampleKbTemplate {
  id: string
  filename: string
  description: string
}

export interface SampleKbBootstrapResponse {
  created: Document[]
  existing: Document[]
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function clearAccessToken() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
}

export function setAccessToken(token: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function hasStoredAccess() {
  return !!localStorage.getItem(ACCESS_TOKEN_KEY)
}

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    const detail = err?.response?.data?.detail
    if (err?.response?.status === 401) clearAccessToken()
    if (detail) err.message = detail
    return Promise.reject(err)
  }
)

export async function getCurrentUser(): Promise<AuthMeResponse> {
  const { data } = await api.get<AuthMeResponse>('/api/auth/me')
  return data
}

export async function getUsage(): Promise<UsageResponse> {
  const { data } = await api.get<UsageResponse>('/api/auth/usage')
  return data
}

export async function uploadDocument(file: File): Promise<Document> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<Document>('/api/documents', form)
  return data
}

export async function getDocuments(): Promise<Document[]> {
  const { data } = await api.get<Document[]>('/api/documents')
  return data
}

export async function getDocument(id: string): Promise<Document> {
  const { data } = await api.get<Document>(`/api/documents/${id}`)
  return data
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/api/documents/${id}`)
}

export async function askQuestion(documentId: string, question: string, mode = 'text'): Promise<QueryResult> {
  const { data } = await api.post<QueryResult>('/api/query', { document_id: documentId, question, mode })
  return data
}

export async function getSampleKbTemplates(): Promise<SampleKbTemplate[]> {
  const { data } = await api.get<SampleKbTemplate[]>('/api/sample-kb')
  return data
}

export async function bootstrapSampleKb(): Promise<SampleKbBootstrapResponse> {
  const { data } = await api.post<SampleKbBootstrapResponse>('/api/sample-kb/bootstrap')
  return data
}
