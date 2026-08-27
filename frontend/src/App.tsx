import { useState } from 'react'
import { BrainPanel } from './components/BrainPanel'
import { AgentOrb } from './components/AgentOrb'
import { useVoiceAgent } from './hooks/useVoiceAgent'
import { AccessGate } from './components/AccessGate'
import { UsageBar } from './components/UsageBar'

export type AgentState = 'idle' | 'user-speaking' | 'thinking' | 'ai-speaking' | 'error'

export default function App() {
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const { agentState, statusMessage, startListening, stopListening, isListening } = useVoiceAgent(selectedDocId)

  return (
    <AccessGate>
      <div className="flex flex-col h-screen bg-[#0a0a1a] overflow-hidden">
        <div className="px-4 pt-3">
          <UsageBar />
        </div>
        {/* BRAIN PANEL - top strip */}
        <BrainPanel selectedDocId={selectedDocId} onSelectDoc={setSelectedDocId} />

        {/* AGENT ORB - fullscreen bottom */}
        <AgentOrb
          state={agentState}
          statusMessage={statusMessage}
          isListening={isListening}
          hasDocument={!!selectedDocId}
          onStartListening={startListening}
          onStopListening={stopListening}
        />
      </div>
    </AccessGate>
  )
}
