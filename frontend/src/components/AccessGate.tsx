import { useEffect, useState, type ReactNode } from 'react'
import { clearAccessToken, getUsage, setAccessToken } from '../api/client'
import { firebaseConfigured, onTokenChange, signInWithGoogle, signOutGoogle } from '../auth/firebase'

interface Props {
  children: ReactNode
}

export function AccessGate({ children }: Props) {
  const [ready, setReady] = useState(false)
  const [authed, setAuthed] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [email, setEmail] = useState<string>('')

  useEffect(() => {
    const unsubscribe = onTokenChange(async (token, user) => {
      if (!token) {
        clearAccessToken()
        setAuthed(false)
        setEmail('')
        setReady(true)
        return
      }

      setAccessToken(token)
      setEmail(user?.email || '')

      try {
        await getUsage()
        setAuthed(true)
        setError(null)
      } catch (err: any) {
        clearAccessToken()
        setAuthed(false)
        setError(err?.message || 'Authentication failed. Please sign in again.')
      } finally {
        setReady(true)
      }
    })

    return () => unsubscribe()
  }, [])

  async function handleGoogleSignIn() {
    setSubmitting(true)
    setError(null)
    try {
      const token = await signInWithGoogle()
      setAccessToken(token)
      await getUsage()
      setAuthed(true)
    } catch (err: any) {
      setError(err?.message || 'Google sign-in failed. Please try again.')
      clearAccessToken()
    } finally {
      setSubmitting(false)
      setReady(true)
    }
  }

  async function handleSignOut() {
    await signOutGoogle()
    clearAccessToken()
    setAuthed(false)
  }

  if (!ready) {
    return <div className="h-screen grid place-items-center text-sm text-slate-400">Loading secure voice workspace…</div>
  }

  if (!authed) {
    return (
      <div className="h-screen grid place-items-center p-4 bg-[#0a0a1a]">
        <div className="w-full max-w-md rounded-xl p-6 bg-[#11112a] border border-[#2a2a5a]">
          <p className="text-xs tracking-widest uppercase font-semibold mb-1 text-purple-300">Voice RAG Support</p>
          <h1 className="text-white text-xl font-bold mb-2">Sign in with Google</h1>
          <p className="text-sm mb-4 text-slate-400">Use your Google account to access this private workspace.</p>

          {!firebaseConfigured && (
            <p className="text-xs mb-3 text-amber-400">
              ⚠ Firebase config missing. Set VITE_FIREBASE_API_KEY, VITE_FIREBASE_AUTH_DOMAIN, VITE_FIREBASE_PROJECT_ID, and VITE_FIREBASE_APP_ID.
            </p>
          )}
          {error && <p className="text-xs mb-3 text-red-400">⚠ {error}</p>}

          <button
            disabled={submitting || !firebaseConfigured}
            onClick={handleGoogleSignIn}
            className="w-full rounded-lg py-2.5 text-sm font-semibold text-white disabled:opacity-60 bg-purple-600"
          >
            {submitting ? 'Signing in...' : 'Continue with Google'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="absolute top-2 right-3 z-50 flex items-center gap-2">
        {email && <span className="text-[11px] text-slate-400">{email}</span>}
        <button onClick={handleSignOut} className="text-[11px] px-2 py-1 rounded bg-slate-700 text-slate-100">
          Sign out
        </button>
      </div>
      {children}
    </>
  )
}
