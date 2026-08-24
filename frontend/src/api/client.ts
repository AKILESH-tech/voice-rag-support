import axios from 'axios'
import type { Document, QueryResult } from '../types'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE })

api.interceptors.response.use(
  r => r,
  err => {
    const detail = err?.response?.data?.detail
    if (detail) err.message = detail
    return Promise.reject(err)
  }
)

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

