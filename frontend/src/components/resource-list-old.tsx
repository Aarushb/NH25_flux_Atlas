import { useEffect, useRef, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { useToast } from './use-toast'

export interface ResourceItem {
  id: string
  name: string
  supply: number
  demand: number
  description?: string
}

interface BidState {
  id: string
  resourceName: string
  seller: string
  sellerUnits: number
  sellerBase: number
  price: number
  quantity: number
  round: number
  status: string | null
  history: Array<{ round: number; price: number; quantity: number; status: string; ts: number }>
  showReceipt: boolean
}

const DUMMY: ResourceItem[] = [
  { id: 'r1', name: 'Aluminum', supply: 12400, demand: 9800, description: 'Bauxite-derived metal used in construction and packaging.' },
  { id: 'r2', name: 'Oil', supply: 540000, demand: 498000, description: 'Crude oil reserves and production capacity.' },
  { id: 'r3', name: 'Natural Gas', supply: 320000, demand: 340000, description: 'Fossil fuel used for power and industry.' },
  { id: 'r4', name: 'Uranium', supply: 4200, demand: 3800, description: 'Fuel for nuclear reactors.' },
]

export default function ResourceList({ resources = DUMMY }: { resources?: ResourceItem[] }) {
  const [selected, setSelected] = useState<ResourceItem | null>(null)
  const [activeBids, setActiveBids] = useState<Record<string, BidState>>({})
  const [currentBidId, setCurrentBidId] = useState<string | null>(null)

  const timersRef = useRef<Record<string, number>>({})

  const toast = useToast()
  const MAX_ROUNDS = 3
  const DECISION_DELAY_MS = 3000
  const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

  const currentBid = currentBidId ? activeBids[currentBidId] : null

  useEffect(() => {
    return () => {
      Object.values(timersRef.current).forEach((t) => clearTimeout(t))
      timersRef.current = {}
    }
  }, [])

  function updateBid(bidId: string, updates: Partial<BidState>) {
    setActiveBids((prev) => ({
      ...prev,
      [bidId]: { ...prev[bidId], ...updates },
    }))
  }

  function startDecisionFor(bidId: string) {
    const bid = activeBids[bidId]
    if (!bid || timersRef.current[bidId]) return

    const currentRound = bid.round
    const currentPrice = bid.price
    const currentQty = bid.quantity

    updateBid(bidId, { status: 'rounding' })

    timersRef.current[bidId] = window.setTimeout(() => {
      delete timersRef.current[bidId]
      const accepted = currentPrice >= bid.sellerBase * (0.9 + Math.random() * 0.2)
      const status = accepted ? 'accepted' : 'rejected'
      const entry = { round: currentRound, price: currentPrice, quantity: currentQty, status, ts: Date.now() }

      setActiveBids((prev) => {
        const updated = { ...prev[bidId] }
        const newHistory = [...updated.history, entry]
        updated.history = newHistory
        updated.status = status

        window.dispatchEvent(new CustomEvent('auction:updated', { detail: { id: bidId, round: currentRound, status } }))
        toast.push({
          title: accepted ? 'Bid accepted' : 'Bid not accepted',
          description: `Decision for round ${currentRound} • ${updated.seller}`,
          level: accepted ? 'success' : 'error',
          timeout: 8000,
        })

        if (currentRound >= MAX_ROUNDS) {
          updated.showReceipt = true
          window.dispatchEvent(
            new CustomEvent('auction:placed', {
              detail: {
                id: bidId,
                resource: updated.resourceName,
                seller: updated.seller,
                rounds: newHistory,
                total: newHistory.reduce((s, r) => s + r.price * r.quantity, 0),
              },
            })
          )
        }

        return { ...prev, [bidId]: updated }
      })
    }, DECISION_DELAY_MS) as unknown as number
  }

  function sellersFor(resourceName: string) {
    const common = [
      { country: 'United States', units: Math.floor(Math.random() * 50000) + 1000, base: 12.5 },
      { country: 'Brazil', units: Math.floor(Math.random() * 30000) + 500, base: 13.2 },
      { country: 'Australia', units: Math.floor(Math.random() * 25000) + 200, base: 11.9 },
      { country: 'China', units: Math.floor(Math.random() * 120000) + 2000, base: 10.3 },
    ]
    if (resourceName.toLowerCase().includes('oil')) return common.slice(1, 4).map((s, i) => ({ ...s, base: s.base + i * 0.6 }))
    if (resourceName.toLowerCase().includes('uranium')) return [common[2], common[3]]
    return common
  }

  function printReceipt(bid: BidState) {
    try {
      const win = window.open('', '_blank', 'width=800,height=900')
      if (!win) return
      const rows = bid.history
        .map(
          (r) => `
        <tr>
          <td style="padding:8px">${r.round}</td>
          <td style="padding:8px">${fmt.format(r.price)}</td>
          <td style="padding:8px">${r.quantity}</td>
          <td style="padding:8px">${new Date(r.ts).toLocaleString()}</td>
          <td style="padding:8px">${r.status}</td>
        </tr>
      `
        )
        .join('')
      const total = fmt.format(bid.history.reduce((s, r) => s + r.price * r.quantity, 0))
      win.document.write(`<!doctype html><html><head><title>Receipt</title><style>body{font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,'Helvetica Neue',Arial;margin:24px;color:#fff;background:#071218}table{border-collapse:collapse;width:100%}th{text-align:left;padding:8px;color:#9ca3af}td{color:#e5e7eb}</style></head><body><h2>Bid receipt</h2><div>Resource: <strong>${bid.resourceName}</strong> • Seller: <strong>${bid.seller}</strong></div><table><thead><tr><th>Round</th><th>Price</th><th>Qty</th><th>When</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table><div style="margin-top:16px;font-weight:700">Total: ${total}</div></body></html>`)
      win.document.close()
      win.focus()
      setTimeout(() => win.print(), 300)
    } catch {
      // ignore
    }
  }

  return (
    <div className="resource-list space-y-3">
      <Card className="glass">
        <CardContent>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Resources</h3>
            <div className="text-xs text-muted-foreground">Click a resource to start trading</div>
          </div>

          <div className="mt-3 overflow-auto">
            <table className="w-full text-base">
              <thead>
                <tr className="text-xs text-muted-foreground text-left">
                  <th className="pb-2">Resource</th>
                  <th className="pb-2">Supply</th>
                  <th className="pb-2">Demand</th>
                </tr>
              </thead>
              <tbody>
                {resources.map((r) => (
                  <tr key={r.id} className="cursor-pointer hover:bg-[rgba(0,255,127,0.03)]" onClick={() => setSelected(r)}>
                    <td className="py-3">{r.name}</td>
                    <td className="py-3 pl-4">{r.supply.toLocaleString()}</td>
                    <td className="py-3 pl-4">{r.demand.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60" onClick={() => setSelected(null)} />
          <div className="w-[1000px] max-w-[98vw] z-60">
            <Card className="glass backdrop-blur-lg bg-white/5 border border-zinc-700">
              <CardContent>
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-2xl font-semibold">{selected.name}</h4>
                    <div className="text-sm text-muted-foreground">Supply & demand overview</div>
                  </div>
                  <div>
                    <button className="btn" onClick={() => setSelected(null)}>
                      Close
                    </button>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Supply</div>
                    <div className="text-3xl font-bold">{selected.supply.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Demand</div>
                    <div className="text-3xl font-bold">{selected.demand.toLocaleString()}</div>
                  </div>
                </div>

                <div className="mt-4 text-sm text-muted-foreground">{selected.description}</div>

                <div className="mt-6">
                  {!currentBidId && (
                    <>
                      <div className="flex items-center justify-between">
                        <h5 className="text-sm font-medium">Sellers</h5>
                        <div className="text-xs text-muted-foreground">Market offers for this resource</div>
                      </div>

                      <div className="mt-3 overflow-auto max-h-64">
                        <table className="w-full text-base">
                          <thead>
                            <tr className="text-xs text-muted-foreground text-left">
                              <th className="pb-2">Country</th>
                              <th className="pb-2">Units</th>
                              <th className="pb-2">Base price</th>
                              <th className="pb-2">Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {sellersFor(selected.name).map((s, i) => (
                              <tr key={i} className="hover:bg-[rgba(0,255,127,0.03)]">
                                <td className="py-3">{s.country}</td>
                                <td className="py-3 pl-4">{s.units.toLocaleString()}</td>
                                <td className="py-3 pl-4">${s.base.toFixed(2)}</td>
                                <td className="py-3">
                                  <button
                                    className="btn btn-sm"
                                    onClick={() => {
                                      const id = Math.random().toString(36).slice(2, 9)
                                      const newBid: BidState = {
                                        id,
                                        resourceName: selected.name,
                                        seller: s.country,
                                        sellerUnits: s.units,
                                        sellerBase: s.base,
                                        price: s.base,
                                        quantity: Math.min(1000, Math.max(10, Math.floor(s.units / 10))),
                                        round: 1,
                                        status: null,
                                        history: [],
                                        showReceipt: false,
                                      }
                                      setActiveBids((prev) => ({ ...prev, [id]: newBid }))
                                      setCurrentBidId(id)
                                      window.dispatchEvent(
                                        new CustomEvent('auction:started', {
                                          detail: {
                                            id,
                                            resource: selected.name,
                                            seller: s.country,
                                            price: s.base,
                                            quantity: newBid.quantity,
                                            round: 1,
                                            status: 'started',
                                          },
                                        })
                                      )
                                    }}
                                  >
                                    Place Bid
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}

                  {currentBidId && currentBid && (
                    <div className="mt-4 border-t pt-4">
                      {!currentBid.showReceipt ? (
                        <>
                          <div className="flex items-center justify-between">
                            <div className="text-3xl font-bold text-white">Round {currentBid.round}</div>
                            <div className="text-xs text-muted-foreground">Country</div>
                          </div>
                          <div className="flex items-center justify-between mt-1">
                            <div className="font-semibold">{currentBid.seller}</div>
                            <div className="text-xs text-muted-foreground">Available: ~{currentBid.sellerUnits}</div>
                          </div>

                          <div className="mt-3 grid grid-cols-2 gap-6">
                            <div className="flex flex-col text-sm text-white gap-2">
                              <div className="font-medium">Price (USD)</div>
                              <input
                                className={`input w-full px-3 py-2 bg-transparent border-zinc-700 text-white text-base ${
                                  currentBid.status === 'rounding' ? 'opacity-60 cursor-not-allowed' : ''
                                }`}
                                type="number"
                                value={currentBid.price}
                                onChange={(e) => updateBid(currentBidId, { price: Number(e.target.value) })}
                                step="0.01"
                                min="0"
                                disabled={currentBid.status === 'rounding'}
                              />
                            </div>

                            <div className="flex flex-col text-sm text-white gap-2">
                              <div className="font-medium">Quantity</div>
                              <input
                                className={`input w-full px-3 py-2 bg-transparent border-zinc-700 text-white text-base ${
                                  currentBid.status === 'rounding' ? 'opacity-60 cursor-not-allowed' : ''
                                }`}
                                type="number"
                                value={currentBid.quantity}
                                onChange={(e) => updateBid(currentBidId, { quantity: Number(e.target.value) })}
                                min={1}
                                max={currentBid.sellerUnits}
                                disabled={currentBid.status === 'rounding'}
                              />
                            </div>
                          </div>

                          <div className="mt-3 flex items-center justify-between">
                            <div className="text-sm text-white">Estimated total:</div>
                            <div className="text-lg font-bold text-white">${(currentBid.price * currentBid.quantity).toFixed(2)}</div>
                          </div>

                          <div className="mt-4 flex items-center gap-2">
                            <button
                              className={`btn ${currentBid.status === 'rounding' ? 'opacity-60 cursor-not-allowed' : 'opacity-80'}`}
                              disabled={
                                currentBid.status === 'rounding' ||
                                !(currentBid.price > 0 && currentBid.quantity > 0 && currentBid.quantity <= currentBid.sellerUnits)
                              }
                              onClick={() => {
                                const alreadyDecidedThisRound = currentBid.history.some((r) => r.round === currentBid.round)
                                if (alreadyDecidedThisRound) {
                                  if (currentBid.round >= MAX_ROUNDS) return
                                  updateBid(currentBidId, { round: currentBid.round + 1, status: null })
                                  return
                                }

                                startDecisionFor(currentBidId)
                              }}
                            >
                              {currentBid.status === 'rounding' ? (
                                <div className="flex items-center gap-2">
                                  <div className="h-4 w-4 rounded-full border-2 border-t-transparent border-green-400 animate-spin" />
                                  <span>Finalising...</span>
                                </div>
                              ) : (
                                'Place'
                              )}
                            </button>
                          </div>

                          <div className="mt-3 max-h-56 overflow-auto">
                            <table className="w-full text-base">
                              <thead>
                                <tr className="text-xs text-muted-foreground text-left">
                                  <th className="pb-2">Round</th>
                                  <th className="pb-2">Price</th>
                                  <th className="pb-2">Qty</th>
                                  <th className="pb-2">When</th>
                                  <th className="pb-2">Status</th>
                                </tr>
                              </thead>
                              <tbody>
                                {currentBid.history.map((r) => (
                                  <tr key={`${r.round}-${r.ts}`} className="odd:bg-black/5">
                                    <td className="py-3">{r.round}</td>
                                    <td className="py-3 pl-4">{fmt.format(r.price)}</td>
                                    <td className="py-3 pl-4">{r.quantity}</td>
                                    <td className="py-3 pl-4">{new Date(r.ts).toLocaleString()}</td>
                                    <td className="py-3 pl-4">{r.status}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          <div className="mt-3 flex items-center justify-end">
                            <div className="text-sm text-white">Total:</div>
                            <div className="ml-3 font-bold text-white">
                              ${currentBid.history.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)}
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="mt-4 bg-[#071218] border border-zinc-800 p-4 rounded">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-sm font-semibold">Bid receipt</div>
                              <div className="text-xs text-muted-foreground">All rounds summary</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="inline-block text-xs bg-zinc-900 text-zinc-200 px-2 py-1 rounded">
                                {currentBid.seller}
                              </span>
                              <button className="btn btn-sm" onClick={() => printReceipt(currentBid)}>
                                Print
                              </button>
                              <button
                                className="btn"
                                onClick={() => {
                                  setActiveBids((prev) => {
                                    const updated = { ...prev }
                                    delete updated[currentBidId]
                                    return updated
                                  })
                                  setCurrentBidId(null)
                                  setSelected(null)
                                }}
                              >
                                Done
                              </button>
                            </div>
                          </div>

                          <div className="mt-3 max-h-56 overflow-auto">
                            <table className="w-full text-base">
                              <thead>
                                <tr className="text-xs text-muted-foreground text-left">
                                  <th className="pb-2">Round</th>
                                  <th className="pb-2">Price</th>
                                  <th className="pb-2">Qty</th>
                                  <th className="pb-2">When</th>
                                  <th className="pb-2">Status</th>
                                </tr>
                              </thead>
                              <tbody>
                                {currentBid.history.map((r) => (
                                  <tr key={`${r.round}-${r.ts}`} className="odd:bg-black/5">
                                    <td className="py-3">{r.round}</td>
                                    <td className="py-3 pl-4">{fmt.format(r.price)}</td>
                                    <td className="py-3 pl-4">{r.quantity}</td>
                                    <td className="py-3 pl-4">{new Date(r.ts).toLocaleString()}</td>
                                    <td className="py-3 pl-4">{r.status}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          <div className="mt-3 flex items-center justify-end">
                            <div className="text-sm text-white">Total:</div>
                            <div className="ml-3 font-bold text-white">
                              ${currentBid.history.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)}
                            </div>
                          </div>
                        </div>
                      )}
                        </table>
                      </div>

                      <div className="mt-3 flex items-center justify-end">
                        <div className="text-sm text-white">Total:</div>
                        <div className="ml-3 font-bold text-white">${roundsHistory.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)}</div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}