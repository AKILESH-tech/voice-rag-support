import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import type { FileRejection } from 'react-dropzone'
import { uploadDocument, getDocuments, deleteDocument } from '../api/client'
import type { Document } from '../types'

const MAX_SIZE_BYTES = 20 * 1024 * 1024 // 20MB
const MAX_SIZE_LABEL = '20MB'

interface Props {
  selectedDocId: string | null
  onSelectDoc: (id: string | null) => void
}

export function BrainPanel({ selectedDocId, onSelectDoc }: Props) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const fetchDocs = useCallback(async () => {
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch {
      // silent — shown in error state
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  // Poll indexing documents
  useEffect(() => {
    const indexing = documents.filter(d => d.status === 'indexing' || d.status === 'pending')
    if (indexing.length === 0) return
    const timer = setInterval(fetchDocs, 2000)
    return () => clearInterval(timer)
  }, [documents, fetchDocs])

  const onDrop = useCallback(async (accepted: File[], rejected: FileRejection[]) => {
    setUploadError(null)
    if (rejected.length > 0) {
      const rej = rejected[0]
      if (rej.errors?.some((e: { code: string }) => e.code === 'file-too-large')) {
        setUploadError(`❌ File too large. Maximum allowed size is ${MAX_SIZE_LABEL}. Please split your PDF or compress it.`)
      } else if (rej.errors?.some((e: { code: string }) => e.code === 'file-invalid-type')) {
        setUploadError('❌ Only PDF files are accepted. Please upload a .pdf file.')
      } else {
        setUploadError('❌ File rejected. Check size (max 20MB) and format (PDF only).')
      }
      return
    }
    if (accepted.length === 0) return

    const file = accepted[0]
    setUploading(true)
    try {
      const doc = await uploadDocument(file)
      setDocuments(prev => [doc, ...prev])
      onSelectDoc(doc.id)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string }
      const msg = e?.response?.data?.detail || e?.message || 'Upload failed'
      setUploadError(`❌ Upload failed: ${msg}`)
    } finally {
      setUploading(false)
    }
  }, [onSelectDoc])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: MAX_SIZE_BYTES,
    multiple: false,
    noClick: uploading,
  })

  const handleDelete = async (doc: Document, e: React.MouseEvent) => {
    e.stopPropagation()
    setDeleteError(null)
    try {
      await deleteDocument(doc.id)
      setDocuments(prev => prev.filter(d => d.id !== doc.id))
      if (selectedDocId === doc.id) onSelectDoc(null)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      const msg = error?.response?.data?.detail || 'Delete failed'
      setDeleteError(`❌ Could not delete: ${msg}`)
    }
  }

  const statusColor = (status: string) => {
    if (status === 'indexed') return 'text-emerald-400'
    if (status === 'failed') return 'text-red-400'
    return 'text-amber-400'
  }

  const statusIcon = (status: string) => {
    if (status === 'indexed') return '✅'
    if (status === 'failed') return '❌'
    return '🔄'
  }

  return (
    <div className="shrink-0 bg-[#0d0d2b] border-b border-[#1e1e4a] px-4 py-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">🧠</span>
          <span className="text-sm font-semibold text-purple-300 tracking-wider uppercase">Brain</span>
          <span className="text-xs text-slate-500">— Knowledge Sources</span>
        </div>
        <div
          {...getRootProps()}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all
            ${isDragActive ? 'bg-purple-600 text-white' : 'bg-purple-900/40 text-purple-300 hover:bg-purple-800/60 border border-purple-700/40'}
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <><span className="animate-spin">⏳</span> Uploading...</>
          ) : isDragActive ? (
            <>📂 Drop PDF here</>
          ) : (
            <>+ Add PDF</>
          )}
        </div>
      </div>

      {/* Limit notice */}
      <p className="text-xs text-slate-500 mb-2">
        📄 PDF only · Max {MAX_SIZE_LABEL} · Select a document to activate the agent
      </p>

      {/* Error messages */}
      {(uploadError || deleteError) && (
        <div className="mb-2 px-3 py-2 bg-red-950/60 border border-red-700/40 rounded-lg text-xs text-red-300 animate-[count-in_0.2s_ease]">
          {uploadError || deleteError}
          <button onClick={() => { setUploadError(null); setDeleteError(null) }} className="ml-2 text-red-400 hover:text-red-200">✕</button>
        </div>
      )}

      {/* Document list */}
      {documents.length === 0 && !uploading && (
        <p className="text-xs text-slate-600 italic">No documents yet. Add a PDF to get started.</p>
      )}

      <div className="flex gap-2 flex-wrap">
        {documents.map(doc => (
          <button
            key={doc.id}
            onClick={() => doc.status === 'indexed' && onSelectDoc(selectedDocId === doc.id ? null : doc.id)}
            disabled={doc.status !== 'indexed'}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs border transition-all
              ${selectedDocId === doc.id
                ? 'bg-purple-700/50 border-purple-500 text-purple-100'
                : doc.status === 'indexed'
                  ? 'bg-[#12122a] border-[#2a2a5a] text-slate-300 hover:border-purple-600'
                  : 'bg-[#0f0f22] border-[#1a1a3a] text-slate-500 cursor-default'
              }`}
          >
            <span>{statusIcon(doc.status)}</span>
            <span className="max-w-[120px] truncate">{doc.filename}</span>
            {doc.page_count && <span className="text-slate-500">{doc.page_count}p</span>}
            <span className={`${statusColor(doc.status)}`}>
              {doc.status === 'indexed' ? '' : doc.status === 'failed' ? 'Failed' : 'Indexing...'}
            </span>
            <button
              onClick={(e) => handleDelete(doc, e)}
              className="ml-1 text-slate-600 hover:text-red-400 transition-colors"
              title="Delete document"
            >🗑</button>
          </button>
        ))}
      </div>
    </div>
  )
}
