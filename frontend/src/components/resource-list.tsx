import { useEffect, useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "./use-toast";

export interface ResourceItem {
  id: string;
  name: string;
  supply: number;
  demand: number;
  description?: string;
}

const DUMMY: ResourceItem[] = [
  { id: "r1", name: "Aluminum", supply: 12400, demand: 9800, description: "Bauxite-derived metal used in construction and packaging." },
  { id: "r2", name: "Oil", supply: 540000, demand: 498000, description: "Crude oil reserves and production capacity." },
  { id: "r3", name: "Natural Gas", supply: 320000, demand: 340000, description: "Fossil fuel used for power and industry." },
  { id: "r4", name: "Uranium", supply: 4200, demand: 3800, description: "Fuel for nuclear reactors." },
];

export default function ResourceList({ resources = DUMMY }: { resources?: ResourceItem[] }) {
  const [selected, setSelected] = useState<ResourceItem | null>(null);
  const [mode, setMode] = useState<'detail' | 'bid'>('detail');
  const [chosenSellerObj, setChosenSellerObj] = useState<{ country: string; units: number; base: number } | null>(null);
  const [bidPrice, setBidPrice] = useState<number | null>(null);
  const [bidQuantity, setBidQuantity] = useState<number>(0);
  const [bidStatus, setBidStatus] = useState<string | null>(null);
  const [round, setRound] = useState<number>(0);
  const [bidId, setBidId] = useState<string | null>(null);
  const [roundsHistory, setRoundsHistory] = useState<Array<{ round: number; price: number; quantity: number; status: string; ts: number }>>([]);
  const [showReceipt, setShowReceipt] = useState(false);
  const [roundsPlaced, setRoundsPlaced] = useState<number[]>([]);
  const placedRef = useRef(false);
  const toast = useToast();
  const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
  function printReceipt() {
    try {
      const win = window.open('', '_blank', 'width=800,height=900')
      if (!win) return
      const rows = roundsHistory.map(r => `
        <tr>
          <td style="padding:8px">${r.round}</td>
          <td style="padding:8px">${fmt.format(r.price)}</td>
          <td style="padding:8px">${r.quantity}</td>
          <td style="padding:8px">${new Date(r.ts).toLocaleString()}</td>
          <td style="padding:8px">${r.status}</td>
        </tr>
      `).join('')
      const total = fmt.format(roundsHistory.reduce((s, r) => s + r.price * r.quantity, 0))
      win.document.write(`<!doctype html><html><head><title>Receipt</title><style>body{font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,'Helvetica Neue',Arial;margin:24px;color:#fff;background:#071218}table{border-collapse:collapse;width:100%}th{text-align:left;padding:8px;color:#9ca3af}td{color:#e5e7eb}</style></head><body><h2>Bid receipt</h2><div>Seller: <strong>${chosenSellerObj?.country ?? ''}</strong></div><table><thead><tr><th>Round</th><th>Price</th><th>Qty</th><th>When</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table><div style="margin-top:16px;font-weight:700">Total: ${total}</div></body></html>`)
      win.document.close()
      win.focus()
      setTimeout(() => win.print(), 300)
    } catch {
      // ignore
    }
  }
  const locked = bidStatus === 'rounding';

  useEffect(() => {
    const onReopen = (e: Event) => {
      const d = (e as CustomEvent).detail
      try {
        const raw = localStorage.getItem('activeBids')
        if (!raw) return
  const parsed = JSON.parse(raw)
  if (!Array.isArray(parsed)) return
  const list = parsed as Array<Record<string, unknown>>
  const found = list.find((b) => (b['id'] as unknown) === d.id) as Record<string, unknown> | undefined
  if (!found) return
  const resourceName = String(found['resource'] ?? '')
  const seller = String(found['seller'] ?? '')
  const price = Number(found['price'] ?? 0)
  const quantity = Number(found['quantity'] ?? 0)
  const rround = Number(found['round'] ?? 1)
  const idv = String(found['id'] ?? '')

  const res = resources.find((r) => r.name === resourceName) ?? { id: '_external', name: resourceName, supply: 0, demand: 0, description: '' }
  setSelected(res)
  setChosenSellerObj({ country: seller, units: quantity, base: price })
  setBidPrice(price)
  setBidQuantity(quantity)
  setRound(rround)
  setBidId(idv)
  setMode('bid')
      } catch {
        // ignore
      }
    }

    window.addEventListener('auction:reopen', onReopen as EventListener)
    return () => window.removeEventListener('auction:reopen', onReopen as EventListener)
  }, [resources])

  useEffect(() => {
    placedRef.current = false
  }, [round])

  function sellersFor(resourceName: string) {
    const common = [
      { country: 'United States', units: Math.floor(Math.random() * 50000) + 1000, base: 12.5 },
      { country: 'Brazil', units: Math.floor(Math.random() * 30000) + 500, base: 13.2 },
      { country: 'Australia', units: Math.floor(Math.random() * 25000) + 200, base: 11.9 },
      { country: 'China', units: Math.floor(Math.random() * 120000) + 2000, base: 10.3 },
    ];
    if (resourceName.toLowerCase().includes('oil')) return common.slice(1, 4).map((s, i) => ({ ...s, base: s.base + i * 0.6 }));
    if (resourceName.toLowerCase().includes('uranium')) return [common[2], common[3]];
    return common;
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
            <Card className="glass">
              <CardContent>
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="text-2xl font-semibold">{selected.name}</h4>
                          <div className="text-sm text-muted-foreground">Supply & demand overview</div>
                        </div>
                        <div>
                          <button className="btn" onClick={() => setSelected(null)}>Close</button>
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
                        {mode === 'detail' && (
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
                                              setBidId(id);
                                              setChosenSellerObj(s);
                                              setBidPrice(s.base);
                                              setBidQuantity(Math.min(1000, Math.max(10, Math.floor(s.units / 10))));
                                              setMode('bid');
                                                setRound(1);
                                                setRoundsHistory([]);
                                              setBidStatus(null);
                                              window.dispatchEvent(new CustomEvent('auction:started', { detail: { id, resource: selected.name, seller: s.country, price: s.base, quantity: Math.min(1000, Math.max(10, Math.floor(s.units / 10))), round: 1, status: 'started' } }))
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

                        {mode === 'bid' && (
                          <div className="mt-4 border-t pt-4">
                            <div className="flex items-center justify-between">
                              <div className="text-xs text-muted-foreground">Round {round}</div>
                              <div className="text-xs text-muted-foreground">Country</div>
                            </div>
                            <div className="flex items-center justify-between mt-1">
                              <div className="font-semibold">{chosenSellerObj?.country}</div>
                              <div className="text-xs text-muted-foreground">Available: ~{chosenSellerObj?.units}</div>
                            </div>

                            <div className="mt-3 grid grid-cols-2 gap-6">
                              <div className="flex flex-col text-sm text-white gap-2">
                                <div className="font-medium">Price (USD)</div>
                                <input
                                  className={`input w-full px-3 py-2 bg-transparent border-zinc-700 text-white text-base ${locked ? 'opacity-60 cursor-not-allowed' : ''}`}
                                  type="number"
                                  value={bidPrice ?? ''}
                                  onChange={(e) => setBidPrice(Number(e.target.value))}
                                  step="0.01"
                                  min="0"
                                  disabled={locked}
                                />
                              </div>

                              <div className="flex flex-col text-sm text-white gap-2">
                                <div className="font-medium">Quantity</div>
                                <input
                                  className={`input w-full px-3 py-2 bg-transparent border-zinc-700 text-white text-base ${locked ? 'opacity-60 cursor-not-allowed' : ''}`}
                                  type="number"
                                  value={bidQuantity}
                                  onChange={(e) => setBidQuantity(Number(e.target.value))}
                                  min={1}
                                  max={chosenSellerObj?.units ?? 999999}
                                  disabled={locked}
                                />
                              </div>
                            </div>

                            <div className="mt-3 flex items-center justify-between">
                              <div className="text-sm text-white">Estimated total:</div>
                              <div className="text-lg font-bold text-white">${((bidPrice ?? 0) * bidQuantity).toFixed(2)}</div>
                            </div>

                            <div className="mt-4 flex items-center gap-2">
                              <button
                                className={`btn ${locked || roundsPlaced.includes(round) || placedRef.current ? 'opacity-60 cursor-not-allowed' : 'opacity-80'}`}
                                disabled={locked || roundsPlaced.includes(round) || placedRef.current || !(bidPrice && bidPrice > 0 && bidQuantity > 0 && bidQuantity <= (chosenSellerObj?.units ?? Infinity))}
                                onClick={async () => {
                                  if (locked || roundsPlaced.includes(round) || placedRef.current) return;
                                  placedRef.current = true;
                                  setRoundsPlaced((p) => Array.from(new Set([...p, round])));
                                  setBidStatus('rounding');
                                  try {
                                    await new Promise((res) => setTimeout(res, 1200));
                                    const base = chosenSellerObj?.base ?? 0;
                                    const threshold = base * (0.9 + Math.random() * 0.2);
                                    const accepted = (bidPrice ?? 0) >= threshold;
                                    const status = accepted ? 'accepted' : 'rejected';
                                    setBidStatus(status);

                                    setRoundsHistory((prev) => [...prev, { round, price: bidPrice ?? 0, quantity: bidQuantity, status, ts: Date.now() }]);

                                    const keep = await toast.showConfirm({ title: accepted ? 'Bid accepted' : 'Bid not accepted', description: `Round ${round} result for ${chosenSellerObj?.country}` });
                                    if (keep) {
                                      const next = round + 1;
                                      setRound(next);
                                      if (bidId) window.dispatchEvent(new CustomEvent('auction:updated', { detail: { id: bidId, round: next, status: 'in-progress' } }));
                                      setBidStatus(null);
                                      placedRef.current = false;
                                    } else {
                                      setShowReceipt(true);
                                      placedRef.current = false;
                                    }
                                  } catch {
                                    setBidStatus('failed');
                                    placedRef.current = false;
                                  }
                                }}
                              >
                                {bidStatus === 'rounding' ? (
                                  <div className="flex items-center gap-2">
                                    <div className="h-4 w-4 rounded-full border-2 border-t-transparent border-green-400 animate-spin" />
                                    <span>Finalising...</span>
                                  </div>
                                ) : (
                                  'Place'
                                )}
                              </button>

                              <button
                                className="btn"
                                onClick={() => {
                                  if (bidId) window.dispatchEvent(new CustomEvent('auction:updated', { detail: { id: bidId, round, status: 'paused' } }));
                                  setMode('detail');
                                  setChosenSellerObj(null);
                                  setBidPrice(null);
                                  setBidQuantity(0);
                                  setBidStatus(null);
                                  setRound(0);
                                  setBidId(null);
                                    setRoundsHistory([]);
                                    placedRef.current = false;
                                }}
                              >
                                Quit
                              </button>

                              {bidStatus === 'accepted' && <div className="ml-2 text-sm text-green-400">Accepted ✓</div>}
                              {bidStatus === 'rejected' && <div className="ml-2 text-sm text-red-400">Not accepted</div>}
                            </div>
                          </div>
                        )}
                      </div>

                      {showReceipt && (
                        <div className="mt-4 bg-[#071218] border border-zinc-800 p-4 rounded">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="text-sm font-semibold">Bid receipt</div>
                              <div className="text-xs text-muted-foreground">All rounds summary</div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="inline-block text-xs bg-zinc-900 text-zinc-200 px-2 py-1 rounded">{chosenSellerObj?.country}</span>
                              <button className="btn btn-sm" onClick={() => setShowReceipt(false)}>Close</button>
                              <button className="btn btn-sm" onClick={() => printReceipt()}>Print</button>
                              <button
                                className="btn"
                                onClick={() => {
                                  if (bidId) window.dispatchEvent(new CustomEvent('auction:placed', { detail: { id: bidId, resource: selected?.name, seller: chosenSellerObj?.country, rounds: roundsHistory, total: roundsHistory.reduce((s, r) => s + r.price * r.quantity, 0) } }));
                                  setSelected(null);
                                  setMode('detail');
                                  setChosenSellerObj(null);
                                  setBidPrice(null);
                                  setBidQuantity(0);
                                  setBidStatus(null);
                                  setRound(0);
                                  setBidId(null);
                                  setRoundsHistory([]);
                                  placedRef.current = false;
                                  setShowReceipt(false);
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
                                {roundsHistory.map((r) => (
                                  <tr key={r.round} className="odd:bg-black/5">
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
                            <div className="ml-3 font-bold text-white">${roundsHistory.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)}</div>
                          </div>
                        </div>
                      )}

              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}