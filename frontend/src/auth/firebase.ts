import { initializeApp, getApps, getApp } from 'firebase/app'
import { GoogleAuthProvider, getAuth, onIdTokenChanged, signInWithPopup, signOut, type User } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

export const firebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.authDomain &&
  firebaseConfig.projectId &&
  firebaseConfig.appId
)

const app = firebaseConfigured ? (getApps().length ? getApp() : initializeApp(firebaseConfig)) : null
const auth = app ? getAuth(app) : null
const provider = new GoogleAuthProvider()

export async function signInWithGoogle(): Promise<string> {
  if (!auth) throw new Error('Firebase config missing. Set VITE_FIREBASE_* variables.')
  const cred = await signInWithPopup(auth, provider)
  return cred.user.getIdToken()
}

export async function signOutGoogle() {
  if (!auth) return
  await signOut(auth)
}

export function onTokenChange(callback: (token: string | null, user: User | null) => void) {
  if (!auth) {
    callback(null, null)
    return () => {}
  }
  return onIdTokenChanged(auth, async (user) => {
    if (!user) {
      callback(null, null)
      return
    }
    const token = await user.getIdToken()
    callback(token, user)
  })
}
