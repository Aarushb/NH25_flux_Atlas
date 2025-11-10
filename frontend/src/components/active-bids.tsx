import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

type ActiveBid = {
  id: string
  resource: string
  seller: string
  price: number
  quantity: number
  round: number
  status: 'started' | 'in-progress' | 'paused' | 'placed' | 'accepted' | 'rejected'
}

export default function ActiveBids() {
  const [open, setOpen] = useState(false)
  const [bids, setBids] = useState<ActiveBid[]>([])

  useEffect(() => {
    try {
      const raw = localStorage.getItem('activeBids')
      if (raw) setBids(JSON.parse(raw))
    } catch {
      // ignore parse errors
    }

    const onStart = (e: Event) => {
      const d = (e as CustomEvent).detail
      setBids((s) => [{ id: d.id, resource: d.resource, seller: d.seller, price: d.price, quantity: d.quantity, round: d.round || 1, status: 'started' }, ...s])
    }
    const onUpdate = (e: Event) => {
      const d = (e as CustomEvent).detail
      setBids((s) => s.map(b => b.id === d.id ? { ...b, round: d.round ?? b.round, status: d.status ?? b.status } : b))
    }
    const onPlaced = (e: Event) => {
      const d = (e as CustomEvent).detail
      setBids((s) => s.map(b => b.id === d.id ? { ...b, round: d.round ?? b.round, status: 'placed' } : b))
    }

    window.addEventListener('auction:started', onStart as EventListener)
    window.addEventListener('auction:updated', onUpdate as EventListener)
    window.addEventListener('auction:placed', onPlaced as EventListener)

    return () => {
      window.removeEventListener('auction:started', onStart as EventListener)
      window.removeEventListener('auction:updated', onUpdate as EventListener)
      window.removeEventListener('auction:placed', onPlaced as EventListener)
    }
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem('activeBids', JSON.stringify(bids))
    } catch {
      // ignore
    }
  }, [bids])

  const active = bids.filter(b => b.status !== 'placed')
  const past = bids.filter(b => b.status === 'placed')

  function reopen(id: string) {
    window.dispatchEvent(new CustomEvent('auction:reopen', { detail: { id } }))
    setOpen(false)
  }

  const panel = (
    <div className="fixed right-4 top-16 w-[360px] z-[9999]">
      <div className="glass rounded border p-3 bg-[#041417] border-zinc-700 text-white shadow-2xl">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-sm">Bids</div>
          <div className="text-xs text-zinc-400">Active — {active.length}</div>
        </div>

        <div className="mt-3 max-h-56 overflow-auto space-y-2">
          {active.length === 0 && <div className="text-sm text-zinc-400">No active bids</div>}
          {active.map((b) => (
            <div key={b.id} className="p-3 border rounded grid grid-cols-6 gap-3 bg-zinc-900/20 border-zinc-800">
              <div className="col-span-3">
                <div className="text-sm font-medium">{b.resource}</div>
                <div className="text-xs text-zinc-400">{b.seller} • Round {b.round}</div>
              </div>
              <div className="col-span-1 text-right font-semibold">${b.price.toFixed(2)}</div>
              <div className="col-span-1 text-right">{b.quantity}</div>
              <div className="col-span-1 text-right flex flex-col items-end gap-2">
                <div className="flex items-center gap-2 text-xs text-zinc-400">
                  <svg className="h-4 w-4 text-zinc-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.2" />
                    <path d="M12 7v5l3 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span className="text-xs text-zinc-400">{b.status}</span>
                </div>
                <button className="btn btn-sm" onClick={() => reopen(b.id)}>Open</button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-3 border-t pt-2 border-zinc-800">
          <div className="text-xs text-zinc-400">History</div>
          <div className="mt-2 max-h-40 overflow-auto space-y-2">
            {past.length === 0 && <div className="text-sm text-zinc-400">No previous bids</div>}
            {past.map((b) => (
              <div key={b.id} className="p-2 border rounded grid grid-cols-6 gap-2 opacity-90 bg-zinc-900/10 border-zinc-800">
                <div className="col-span-3">
                  <div className="text-sm font-medium">{b.resource}</div>
                  <div className="text-xs text-zinc-400">{b.seller} • Round {b.round}</div>
                </div>
                <div className="col-span-1 text-right font-semibold">${b.price.toFixed(2)}</div>
                <div className="col-span-1 text-right">{b.quantity}</div>
                <div className="col-span-1 text-right text-sm text-zinc-400 flex items-center justify-end gap-2">
                  <svg className="h-4 w-4 text-zinc-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                    <path d="M12 7v5l3 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.2" />
                  </svg>
                  <span className="text-xs text-zinc-400">{b.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="relative">
      <button className="btn btn-ghost relative px-3 py-1" onClick={() => setOpen((o) => !o)} aria-label="Active bids">
        <svg className="h-5 w-5 text-zinc-100" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
          <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.2" />
          <path d="M12 8v5l3 2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {active.length > 0 && <span className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 inline-block h-2 w-2 rounded-full bg-red-500 ring-2 ring-black" />}
      </button>

      {open && typeof document !== 'undefined' ? createPortal(panel, document.body) : null}
    </div>
  )
}
