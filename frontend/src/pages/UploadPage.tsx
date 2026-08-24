import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDocument, getDocument } from '../api/client';
import type { Document } from '../types';

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [doc, setDoc] = useState<Document | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!doc || doc.status === 'indexed' || doc.status === 'failed') return;
    const interval = setInterval(async () => {
      try {
        const updated = await getDocument(doc.id);
        setDoc(updated);
        if (updated.status === 'indexed' || updated.status === 'failed') {
          clearInterval(interval);
        }
      } catch {}
    }, 2000);
    return () => clearInterval(interval);
  }, [doc]);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setError('Please upload a PDF file.');
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const result = await uploadDocument(file);
      setDoc(result as Document);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="max-w-xl mx-auto mt-16 px-4">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-700">📄 Voice RAG Support</h1>
      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="text-5xl mb-4">📁</div>
        <p className="text-gray-600 text-lg">Drag & drop a PDF here or click to browse</p>
        <p className="text-gray-400 text-sm mt-2">Max 20MB • PDF only</p>
        <input ref={fileInputRef} type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
      </div>

      {uploading && <div className="mt-4 text-center text-blue-600 animate-pulse">Uploading & indexing...</div>}

      {error && <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700">{error}</div>}

      {doc && (
        <div className={`mt-6 p-4 rounded-lg border ${doc.status === 'indexed' ? 'bg-green-50 border-green-200' : doc.status === 'failed' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'}`}>
          <p className="font-semibold">{doc.filename}</p>
          <p className="text-sm text-gray-600">Status: <span className="font-medium">{doc.status}</span></p>
          {doc.status === 'pending' && <p className="text-sm text-gray-500 animate-pulse">Indexing in progress...</p>}
          {doc.status === 'indexed' && (
            <>
              <p className="text-sm text-gray-600">{doc.page_count} pages · {doc.chunk_count} chunks</p>
              <button
                onClick={() => navigate('/chat', { state: { documentId: doc.id } })}
                className="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
              >
                Start Chatting →
              </button>
            </>
          )}
          {doc.status === 'failed' && <p className="text-sm text-red-600">Indexing failed. Please try again.</p>}
        </div>
      )}
    </div>
  );
}
