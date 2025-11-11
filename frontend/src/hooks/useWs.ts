import { useEffect, useState, useCallback } from 'react'
import { wsClient } from '@/lib/ws'
import type { WSMsg } from '@/lib/ws'

export function useWs() {
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    
    const onAny = () => setConnected(true)
    const onClose = () => setConnected(false)
    window.addEventListener('auction:simulated', onAny as EventListener)
    window.addEventListener('ws:message', onAny as EventListener)
    window.addEventListener('ws:closed', onClose as EventListener)
    return () => {
      window.removeEventListener('auction:simulated', onAny as EventListener)
      window.removeEventListener('ws:message', onAny as EventListener)
      window.removeEventListener('ws:closed', onClose as EventListener)
    }
  }, [])

  const send = useCallback((msg: WSMsg, opts?: { private?: boolean }) => {
    return wsClient.send(msg, opts)
  }, [])

  return { connected, send }
}
