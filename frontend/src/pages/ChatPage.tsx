import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getDocuments, askQuestion } from '../api/client';
import type { Document, ChatMessage, QueryResult } from '../types';
import ResultPanel from '../components/ResultPanel';
import TelemetryBar from '../components/TelemetryBar';

export default function ChatPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>((location.state as any)?.documentId || '');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getDocuments().then((docs) => {
      setDocuments(docs.filter(d => d.status === 'indexed'));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim() || !selectedDocId || loading) return;
    const question = input.trim();
    setInput('');
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: question, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const result: QueryResult = await askQuestion(selectedDocId, question);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.answer,
        result,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e: any) {
      const errMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${e?.response?.data?.detail || 'Something went wrong'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError('Web Speech API not available in this browser. Please type your question.');
      return;
    }
    setVoiceError(null);
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => { setListening(false); setVoiceError('Speech recognition error. Please try again.'); };
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };
    recognition.start();
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto px-4">
      <div className="flex items-center justify-between py-4 border-b">
        <h1 className="text-xl font-bold text-blue-700">💬 RAG Chat</h1>
        <button onClick={() => navigate('/')} className="text-sm text-gray-500 hover:text-gray-700">← Upload</button>
      </div>

      <div className="py-3 border-b">
        <select
          value={selectedDocId}
          onChange={e => setSelectedDocId(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
        >
          <option value="">Select a document...</option>
          {documents.map(d => (
            <option key={d.id} value={d.id}>{d.filename} ({d.page_count}p)</option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-16">
            <div className="text-4xl mb-3">🤖</div>
            <p>Select a document and ask a question to get started.</p>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border shadow-sm'}`}>
              {msg.role === 'assistant' && msg.result ? (
                <div className="space-y-3">
                  <ResultPanel result={msg.result} />
                  <TelemetryBar timings={msg.result.timings} />
                </div>
              ) : (
                <p>{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl px-4 py-3 text-gray-500 animate-pulse">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {voiceError && <div className="text-xs text-red-500 px-2">{voiceError}</div>}

      <div className="py-4 border-t">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }}
            placeholder={selectedDocId ? 'Ask a question about the document...' : 'Select a document first'}
            rows={2}
            disabled={!selectedDocId || loading}
            className="flex-1 border rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-50"
          />
          <div className="flex flex-col gap-2">
            <button
              onClick={handleVoice}
              disabled={!selectedDocId || listening || loading}
              className={`px-3 py-2 rounded-xl text-sm transition-colors ${listening ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 hover:bg-gray-200'}`}
              title="Voice input"
            >
              {listening ? '🔴' : '🎤'}
            </button>
            <button
              onClick={handleSubmit}
              disabled={!input.trim() || !selectedDocId || loading}
              className="px-3 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
