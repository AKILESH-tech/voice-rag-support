import { useState, useRef, useCallback } from 'react'
import { askQuestion } from '../api/client'
import type { AgentState } from '../App'

export function useVoiceAgent(documentId: string | null) {
  const [agentState, setAgentState] = useState<AgentState>('idle')
  const [statusMessage, setStatusMessage] = useState('Ask me anything about your documents')
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<{ stop: () => void } | null>(null)
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null)

  const speakAnswer = useCallback((text: string) => {
    setAgentState('ai-speaking')
    setStatusMessage('Speaking...')
    window.speechSynthesis.cancel()
    const utter = new SpeechSynthesisUtterance(text)
    utter.rate = 1.0
    utter.pitch = 1.0
    utter.onend = () => {
      setAgentState('idle')
      setStatusMessage('Ask me anything about your documents')
    }
    utter.onerror = () => {
      setAgentState('idle')
      setStatusMessage('Ask me anything about your documents')
    }
    synthRef.current = utter
    window.speechSynthesis.speak(utter)
  }, [])

  const handleTranscript = useCallback(async (transcript: string) => {
    if (!documentId) {
      setAgentState('error')
      setStatusMessage('Please select a document in Brain first')
      setTimeout(() => { setAgentState('idle'); setStatusMessage('Ask me anything about your documents') }, 3000)
      return
    }
    setAgentState('thinking')
    setStatusMessage(`You asked: "${transcript.substring(0, 60)}${transcript.length > 60 ? '...' : ''}"`)
    try {
      const result = await askQuestion(documentId, transcript, 'voice')
      speakAnswer(result.answer)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string }
      const msg = e?.response?.data?.detail || 'Something went wrong. Please try again.'
      setAgentState('error')
      setStatusMessage(msg)
      speakAnswer(msg)
      setTimeout(() => { setAgentState('idle'); setStatusMessage('Ask me anything about your documents') }, 4000)
    }
  }, [documentId, speakAnswer])

  const startListening = useCallback(() => {
    if (!documentId) {
      setAgentState('error')
      setStatusMessage('☝️ Select a PDF in Brain first')
      setTimeout(() => { setAgentState('idle'); setStatusMessage('Ask me anything about your documents') }, 3000)
      return
    }
    window.speechSynthesis.cancel()
    const SpeechRecognition = (window as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).SpeechRecognition
      || (window as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).webkitSpeechRecognition
    if (!SpeechRecognition) {
      setAgentState('error')
      setStatusMessage('Voice not supported in this browser. Try Chrome.')
      setTimeout(() => { setAgentState('idle'); setStatusMessage('Ask me anything about your documents') }, 4000)
      return
    }
    const RecognitionClass = SpeechRecognition as new () => {
      lang: string
      interimResults: boolean
      maxAlternatives: number
      onresult: ((e: { results: { [key: number]: { [key: number]: { transcript: string } } } }) => void) | null
      onerror: ((e: { error: string }) => void) | null
      onend: (() => void) | null
      start: () => void
      stop: () => void
    }
    const recognition = new RecognitionClass()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      handleTranscript(transcript)
    }
    recognition.onerror = (e) => {
      setAgentState('error')
      const errMap: Record<string, string> = {
        'no-speech': 'No speech detected. Try again.',
        'audio-capture': 'Microphone not found or blocked.',
        'not-allowed': 'Microphone permission denied. Allow mic access.',
        'network': 'Network error during recognition.',
      }
      setStatusMessage(errMap[e.error] || `Recognition error: ${e.error}`)
      setTimeout(() => { setAgentState('idle'); setStatusMessage('Ask me anything about your documents') }, 4000)
      setIsListening(false)
    }
    recognition.onend = () => setIsListening(false)
    recognitionRef.current = recognition
    recognition.start()
    setIsListening(true)
    setAgentState('user-speaking')
    setStatusMessage('Listening...')
  }, [documentId, handleTranscript])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [])

  return { agentState, statusMessage, isListening, startListening, stopListening }
}
