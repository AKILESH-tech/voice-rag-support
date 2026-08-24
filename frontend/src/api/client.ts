import axios from 'axios';
import type { Document, QueryResult } from '../types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000,
});

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<Document>('/api/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getDocuments(): Promise<Document[]> {
  const { data } = await apiClient.get<Document[]>('/api/documents');
  return data;
}

export async function getDocument(id: string): Promise<Document> {
  const { data } = await apiClient.get<Document>(`/api/documents/${id}`);
  return data;
}

export async function askQuestion(
  documentId: string,
  question: string,
  mode: string = 'text'
): Promise<QueryResult> {
  const { data } = await apiClient.post<QueryResult>('/api/query', {
    document_id: documentId,
    question,
    mode,
  });
  return data;
}

export async function getQuery(id: string): Promise<QueryResult> {
  const { data } = await apiClient.get<QueryResult>(`/api/queries/${id}`);
  return data;
}
