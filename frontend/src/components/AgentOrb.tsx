import { motion, AnimatePresence } from 'framer-motion'
import type { AgentState } from '../App'

interface Props {
  state: AgentState
  statusMessage: string
  isListening: boolean
  hasDocument: boolean
  onStartListening: () => void
  onStopListening: () => void
}

const orbConfig: Record<AgentState, { primary: string; secondary: string; glow: string; label: string; icon: string }> = {
  idle: {
    primary: '#1a1a6e',
    secondary: '#2d2d9f',
    glow: '#3333cc',
    label: 'Ready to listen',
    icon: '🎙',
  },
  'user-speaking': {
    primary: '#064e3b',
    secondary: '#047857',
    glow: '#10b981',
    label: 'Listening...',
    icon: '🎤',
  },
  thinking: {
    primary: '#78350f',
    secondary: '#b45309',
    glow: '#f59e0b',
    label: 'Thinking...',
    icon: '💭',
  },
  'ai-speaking': {
    primary: '#7c2d12',
    secondary: '#c2410c',
    glow: '#f97316',
    label: 'Speaking...',
    icon: '🔊',
  },
  error: {
    primary: '#7f1d1d',
    secondary: '#b91c1c',
    glow: '#ef4444',
    label: 'Error occurred',
    icon: '⚠️',
  },
}

export function AgentOrb({ state, statusMessage, isListening, hasDocument, onStartListening, onStopListening }: Props) {
  const cfg = orbConfig[state]

  return (
    <div className="flex-1 flex flex-col items-center justify-center relative overflow-hidden bg-[#080818]">
      {/* Background ambient glow */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{ opacity: state === 'idle' ? 0.15 : 0.3 }}
        style={{
          background: `radial-gradient(ellipse 60% 50% at 50% 60%, ${cfg.glow}44, transparent 70%)`,
        }}
        transition={{ duration: 0.8 }}
      />

      {/* Outer ripple rings — only when user speaking */}
      {state === 'user-speaking' && [1, 2, 3].map(i => (
        <motion.div
          key={i}
          className="absolute rounded-full border-2 border-emerald-500/30"
          initial={{ width: 220, height: 140, opacity: 0.8 }}
          animate={{ width: 220 + i * 80, height: 140 + i * 50, opacity: 0 }}
          transition={{ duration: 1.5, delay: i * 0.3, repeat: Infinity, ease: 'easeOut' }}
          style={{ borderRadius: '50%' }}
        />
      ))}

      {/* AI speaking wave rings */}
      {state === 'ai-speaking' && [1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: 220 + i * 60,
            height: 140 + i * 40,
            border: `2px solid ${cfg.glow}55`,
            borderRadius: '50%',
          }}
          animate={{ scale: [1, 1.12, 1], opacity: [0.6, 0.2, 0.6] }}
          transition={{ duration: 1.2, delay: i * 0.4, repeat: Infinity }}
        />
      ))}

      {/* Main Orb */}
      <motion.div
        className="relative flex items-center justify-center cursor-pointer select-none"
        style={{ width: 220, height: 140 }}
        animate={
          state === 'idle'
            ? { scale: [1, 1.04, 1] }
            : state === 'thinking'
              ? { rotate: [0, 360] }
              : { scale: 1 }
        }
        transition={
          state === 'idle'
            ? { duration: 3, repeat: Infinity, ease: 'easeInOut' }
            : state === 'thinking'
              ? { duration: 3, repeat: Infinity, ease: 'linear' }
              : { duration: 0.3 }
        }
        onMouseDown={hasDocument && state === 'idle' ? onStartListening : undefined}
        onMouseUp={isListening ? onStopListening : undefined}
        onTouchStart={hasDocument && state === 'idle' ? onStartListening : undefined}
        onTouchEnd={isListening ? onStopListening : undefined}
      >
        {/* Orb body */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{ borderRadius: '50%' }}
          animate={{ background: `radial-gradient(ellipse at 35% 35%, ${cfg.secondary}, ${cfg.primary})` }}
          transition={{ duration: 0.6 }}
        />

        {/* Inner shine */}
        <div
          className="absolute inset-0 rounded-full opacity-30"
          style={{
            borderRadius: '50%',
            background: 'radial-gradient(ellipse at 30% 25%, rgba(255,255,255,0.4), transparent 60%)',
          }}
        />

        {/* Glow border */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{ borderRadius: '50%', border: `2px solid ${cfg.glow}` }}
          animate={{ boxShadow: `0 0 40px ${cfg.glow}88, 0 0 80px ${cfg.glow}44, inset 0 0 30px ${cfg.glow}22` }}
          transition={{ duration: 0.6 }}
        />

        {/* Icon */}
        <motion.span
          className="relative z-10 text-3xl"
          key={state}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {state === 'thinking'
            ? <span className="block animate-spin">⚙️</span>
            : cfg.icon}
        </motion.span>
      </motion.div>

      {/* Status message */}
      <AnimatePresence mode="wait">
        <motion.p
          key={statusMessage}
          className="mt-8 text-sm tracking-wide text-center max-w-xs px-4"
          style={{ color: cfg.glow }}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.3 }}
        >
          {statusMessage}
        </motion.p>
      </AnimatePresence>

      {/* No document selected prompt */}
      {!hasDocument && (
        <motion.p
          className="mt-3 text-xs text-slate-600"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          ☝️ Select or upload a PDF in Brain to activate
        </motion.p>
      )}

      {/* Hold to speak hint */}
      {hasDocument && state === 'idle' && (
        <motion.p
          className="mt-3 text-xs text-slate-500"
          animate={{ opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Hold the orb to speak
        </motion.p>
      )}
    </div>
  )
}
