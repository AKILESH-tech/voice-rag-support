import { useEffect, useState } from 'react'
import { getUsage, type UsageResponse } from '../api/client'

export function UsageBar() {
  const [usage, setUsage] = useState<UsageResponse | null>(null)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const data = await getUsage()
        if (mounted) setUsage(data)
      } catch {
        if (mounted) setUsage(null)
      }
    }
    load()
    const timer = setInterval(load, 15000)
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  if (!usage) return null
  const percent = Math.min(100, Math.round((usage.used / usage.limit) * 100))

  return (
    <div className="px-3 py-2 rounded-lg bg-[#12122a] border border-[#2a2a5a]">
      <div className="flex items-center justify-between text-xs mb-1.5">
        <span className="text-purple-300">Daily AI limit</span>
        <span className="text-slate-400">{usage.remaining}/{usage.limit} left</span>
      </div>
      <div className="h-1.5 rounded-full bg-[#1c1c3a]">
        <div className="h-1.5 rounded-full" style={{ width: `${percent}%`, background: usage.remaining > 0 ? '#7c3aed' : '#ef4444' }} />
      </div>
    </div>
  )
}
