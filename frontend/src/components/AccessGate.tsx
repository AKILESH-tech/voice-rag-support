import { useEffect, useState, type ReactNode } from 'react'
import { hasValidStoredAccess, verifyAccess, setAccessToken, clearAccessToken, getUsage } from '../api/client'

interface Props {
  children: ReactNode
}

export function AccessGate({ children }: Props) {
  const [ready, setReady] = useState(false)
  const [authed, setAuthed] = useState(false)
  const [passcode, setPasscode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const init = async () => {
      if (!hasValidStoredAccess()) {
        clearAccessToken()
        setReady(true)
        return
      }
      try {
        await getUsage()
        setAuthed(true)
      } catch {
        clearAccessToken()
      } finally {
        setReady(true)
      }
    }
    init()
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const result = await verifyAccess(passcode.trim())
      setAccessToken(result.token, result.valid_until)
      setAuthed(true)
    } catch (err: any) {
      setError(err?.message || 'Invalid access code. Please try again.')
      clearAccessToken()
    } finally {
      setSubmitting(false)
    }
  }

  if (!ready) {
    return <div className="h-screen grid place-items-center text-sm text-slate-400">Loading secure voice workspace…</div>
  }

  if (!authed) {
    return (
      <div className="h-screen grid place-items-center p-4 bg-[#0a0a1a]">
        <form onSubmit={handleSubmit} className="w-full max-w-md rounded-xl p-6 bg-[#11112a] border border-[#2a2a5a]">
          <p className="text-xs tracking-widest uppercase font-semibold mb-1 text-purple-300">Voice RAG Support</p>
          <h1 className="text-white text-xl font-bold mb-2">Enter access code</h1>
          <p className="text-sm mb-4 text-slate-400">Private demo workspace. Enter the shared passcode to continue.</p>
          <input
            type="password"
            value={passcode}
            onChange={(e) => setPasscode(e.target.value)}
            placeholder="Access code"
            className="w-full rounded-lg px-3 py-2.5 text-sm outline-none mb-3 bg-[#0a0a1a] border border-[#2a2a5a] text-slate-100"
            required
          />
          {error && <p className="text-xs mb-3 text-red-400">⚠ {error}</p>}
          <button
            disabled={submitting}
            className="w-full rounded-lg py-2.5 text-sm font-semibold text-white disabled:opacity-60 bg-purple-600"
          >
            {submitting ? 'Verifying...' : 'Unlock'}
          </button>
        </form>
      </div>
    )
  }

  return <>{children}</>
}
