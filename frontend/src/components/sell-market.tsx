import { useEffect, useRef, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { useToast } from './use-toast'

interface ResourceOption {
  id: string
  name: string
  available: boolean
  nationalReserve?: number
}

interface MarketData {
  timestamp: number
  price: number
}

interface ClusterBid {
  clusterId: number
  countryBids: Array<{ 
    countryId: number
    countryName: string
    amount: number
    timestamp: number
    accepted?: boolean
    droppedOut?: boolean
    bidSubmitted?: boolean
  }>
  currentRound: number
  highestBid: number
  leadingCountry: number
  bidVelocity?: number
  momentum?: number
  bidsSubmitted?: number
  totalCountries?: number
}

interface SaleState {
  resourceId: string
  resourceName: string
  basePrice: number
  units: number
  status: 'setup' | 'verifying' | 'live' | 'completed'
  marketHistory: MarketData[]
  clusterBids: ClusterBid[]
  currentRound: number
  roundWinners: Array<{ clusterId: number; winningBid: number; round: number }>
  totalRevenue: number
  avgWinningBid: number
}

const ALL_RESOURCES: ResourceOption[] = [
  { id: 'r1', name: 'Aluminum', available: true, nationalReserve: 45000 },
  { id: 'r2', name: 'Oil', available: true, nationalReserve: 120000 },
  { id: 'r3', name: 'Natural Gas', available: false, nationalReserve: 800 },
  { id: 'r4', name: 'Uranium', available: true, nationalReserve: 8500 },
  { id: 'r5', name: 'Lithium', available: false, nationalReserve: 120 },
  { id: 'r6', name: 'Copper', available: true, nationalReserve: 32000 },
  { id: 'r7', name: 'Rare Earth Elements', available: false, nationalReserve: 45 },
  { id: 'r8', name: 'Gold', available: true, nationalReserve: 1200 },
]

const MAJOR_EXPORTERS = [
  { country: 'China', units: 2450000, trend: '+12%' },
  { country: 'Saudi Arabia', units: 1980000, trend: '+8%' },
  { country: 'United States', units: 1750000, trend: '+5%' },
]

const COUNTRY_NAMES = [
  'Brazil', 'India', 'Germany', 'France', 'Japan', 'South Korea', 'Canada',
  'Australia', 'Mexico', 'Indonesia', 'Turkey', 'Netherlands', 'Spain',
  'Italy', 'Poland', 'Thailand', 'Malaysia', 'Vietnam', 'Egypt', 'Argentina',
  'Nigeria', 'South Africa', 'Pakistan', 'Bangladesh', 'Philippines',
  'Colombia', 'Chile', 'Peru', 'Ukraine', 'Romania', 'Czech Republic',
  'Belgium', 'Sweden', 'Austria', 'Switzerland', 'Norway', 'Denmark',
  'Finland', 'Portugal', 'Greece', 'Hungary', 'Israel', 'Singapore',
]

export default function SellMarket() {
  const [selectedResource, setSelectedResource] = useState<ResourceOption | null>(null)
  const [saleState, setSaleState] = useState<SaleState | null>(null)
  const [loadingStep, setLoadingStep] = useState(0)
  const [basePrice, setBasePrice] = useState<number>(0)
  const [units, setUnits] = useState<number>(0)

  const chartIntervalRef = useRef<number | null>(null)
  const bidIntervalRef = useRef<number | null>(null)
  const roundTimerRef = useRef<number | null>(null)
  const toast = useToast()

  const MAX_ROUNDS = 5
  const DECISION_DELAY_MS = 3000
  const COUNTRIES_PER_CLUSTER = 7
  const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

  useEffect(() => {
    if (saleState?.status === 'setup' && selectedResource) {
      // generate initial market history
      const history: MarketData[] = []
      const now = Date.now()
      const baseValue = Math.random() * 50 + 50
      for (let i = 180; i >= 0; i--) {
        history.push({
          timestamp: now - i * 24 * 60 * 60 * 1000,
          price: baseValue + Math.sin(i / 10) * 10 + Math.random() * 5,
        })
      }
      setSaleState((prev) => (prev ? { ...prev, marketHistory: history } : prev))

      // start updating chart
      chartIntervalRef.current = window.setInterval(() => {
        setSaleState((prev) => {
          if (!prev) return prev
          const newHistory = [...prev.marketHistory]
          newHistory.shift()
          newHistory.push({
            timestamp: Date.now(),
            price: prev.marketHistory[prev.marketHistory.length - 1].price + (Math.random() - 0.5) * 3,
          })
          return { ...prev, marketHistory: newHistory }
        })
      }, 500)
    }

    return () => {
      if (chartIntervalRef.current) clearInterval(chartIntervalRef.current)
    }
  }, [saleState?.status, selectedResource])

  useEffect(() => {
    if (saleState?.status === 'verifying') {
      const steps = ['Verifying metrics', 'Aggregating clusters', 'Setting up final auction']
      let step = 0
      const timer = setInterval(() => {
        if (step < steps.length) {
          setLoadingStep(step)
          step++
        } else {
          clearInterval(timer)
          setSaleState((prev) =>
            prev
              ? {
                  ...prev,
                  status: 'live',
                  currentRound: 1,
                  roundWinners: [],
                  totalRevenue: 0,
                  avgWinningBid: 0,
                  clusterBids: Array.from({ length: 6 }, (_, i) => {
                    const usedCountries = new Set<string>()
                    const countryBids = Array.from({ length: COUNTRIES_PER_CLUSTER }, (__, idx) => {
                      let countryName = COUNTRY_NAMES[Math.floor(Math.random() * COUNTRY_NAMES.length)]
                      while (usedCountries.has(countryName)) {
                        countryName = COUNTRY_NAMES[Math.floor(Math.random() * COUNTRY_NAMES.length)]
                      }
                      usedCountries.add(countryName)
                      return {
                        countryId: idx,
                        countryName,
                        amount: prev.basePrice + Math.random() * 15 + 5,
                        timestamp: Date.now(),
                        bidSubmitted: false,
                      }
                    })
                    return {
                      clusterId: i + 1,
                      countryBids,
                      currentRound: 1,
                      highestBid: 0,
                      leadingCountry: 0,
                      bidsSubmitted: 0,
                      totalCountries: COUNTRIES_PER_CLUSTER,
                    }
                  }),
                }
              : prev
          )
        }
      }, 1666)

      return () => clearInterval(timer)
    }
  }, [saleState?.status, COUNTRIES_PER_CLUSTER])

  useEffect(() => {
    if (saleState?.status === 'live' && saleState.currentRound <= MAX_ROUNDS) {
      bidIntervalRef.current = window.setInterval(() => {
        setSaleState((prev) => {
          if (!prev || prev.status !== 'live') return prev
          
          const newBids = prev.clusterBids.map((cluster) => {
            const updatedCountryBids = cluster.countryBids.map((bid) => {
              if (bid.droppedOut || bid.bidSubmitted) return bid
              
              if (!bid.droppedOut && !bid.bidSubmitted && Math.random() < 0.05) {
                toast.push({
                  title: 'Country Withdrew',
                  description: `${bid.countryName} from Cluster ${cluster.clusterId} has withdrawn from bidding`,
                  level: 'error',
                  timeout: 4000,
                })
                return { ...bid, droppedOut: true }
              }
              
              if (!bid.bidSubmitted && Math.random() < 0.25) {
                return {
                  ...bid,
                  bidSubmitted: true,
                  timestamp: Date.now(),
                }
              }
              
              return bid
            })
            
            const activeBids = updatedCountryBids.filter((b) => !b.droppedOut && b.bidSubmitted)
            const highest = activeBids.length > 0 ? Math.max(...activeBids.map((b) => b.amount)) : 0
            const leadingIdx = updatedCountryBids.findIndex((b) => b.amount === highest && !b.droppedOut && b.bidSubmitted)
            const bidsSubmitted = updatedCountryBids.filter((b) => b.bidSubmitted || b.droppedOut).length
            const totalCountries = updatedCountryBids.filter((b) => !b.droppedOut).length
            
            return {
              ...cluster,
              countryBids: updatedCountryBids,
              highestBid: highest,
              leadingCountry: leadingIdx,
              bidsSubmitted,
              totalCountries,
            }
          })
          
          const allBidsIn = newBids.every((c) => c.bidsSubmitted === c.totalCountries)
          
          if (allBidsIn && roundTimerRef.current === null) {
            roundTimerRef.current = window.setTimeout(() => {
              setSaleState((p) => {
                if (!p || p.status !== 'live') return p
                
                const winners = p.clusterBids.map((c, idx) => ({
                  clusterId: idx + 1,
                  winningBid: c.highestBid,
                  round: p.currentRound,
                }))
                
                const newRevenue = winners.reduce((sum, w) => sum + w.winningBid, 0)
                const totalRev = p.totalRevenue + newRevenue
                const totalWinners = p.roundWinners.length + winners.length
                const avgBid = totalWinners > 0 ? totalRev / totalWinners : 0
                
                const nextRound = p.currentRound + 1
                
                if (nextRound > MAX_ROUNDS) {
                  if (bidIntervalRef.current !== null) clearInterval(bidIntervalRef.current)
                  return {
                    ...p,
                    status: 'completed',
                    roundWinners: [...p.roundWinners, ...winners],
                    totalRevenue: totalRev,
                    avgWinningBid: avgBid,
                  }
                }
                
                const newClusterBids = p.clusterBids.map((cluster) => {
                  const usedCountries = new Set<string>()
                  return {
                    ...cluster,
                    countryBids: Array.from({ length: COUNTRIES_PER_CLUSTER }, (_, idx) => {
                      let countryName = COUNTRY_NAMES[Math.floor(Math.random() * COUNTRY_NAMES.length)]
                      while (usedCountries.has(countryName)) {
                        countryName = COUNTRY_NAMES[Math.floor(Math.random() * COUNTRY_NAMES.length)]
                      }
                      usedCountries.add(countryName)
                      return {
                        countryId: idx,
                        countryName,
                        amount: p.basePrice + Math.random() * 20 + 8,
                        timestamp: Date.now(),
                        bidSubmitted: false,
                      }
                    }),
                    currentRound: nextRound,
                    highestBid: 0,
                    leadingCountry: 0,
                    bidsSubmitted: 0,
                    totalCountries: COUNTRIES_PER_CLUSTER,
                  }
                })
                
                roundTimerRef.current = null
                
                return {
                  ...p,
                  currentRound: nextRound,
                  clusterBids: newClusterBids,
                  roundWinners: [...p.roundWinners, ...winners],
                  totalRevenue: totalRev,
                  avgWinningBid: avgBid,
                }
              })
            }, DECISION_DELAY_MS)
          }
          
          return {
            ...prev,
            clusterBids: newBids,
          }
        })
      }, 500)

      return () => {
        if (bidIntervalRef.current !== null) clearInterval(bidIntervalRef.current)
        if (roundTimerRef.current !== null) clearTimeout(roundTimerRef.current)
      }
    }
  }, [saleState?.status, saleState?.currentRound, COUNTRIES_PER_CLUSTER, DECISION_DELAY_MS, MAX_ROUNDS, toast])

  function startSale() {
    if (!selectedResource || basePrice <= 0 || units <= 0) {
      toast.push({ title: 'Invalid input', description: 'Please set base price and units', level: 'error', timeout: 3000 })
      return
    }

    setSaleState({
      resourceId: selectedResource.id,
      resourceName: selectedResource.name,
      basePrice,
      units,
      status: 'verifying',
      marketHistory: [],
      clusterBids: [],
      currentRound: 0,
      roundWinners: [],
      totalRevenue: 0,
      avgWinningBid: 0,
    })
  }

  const loadingSteps = ['Verifying metrics', 'Aggregating clusters', 'Setting up final auction']

  return (
    <div className="sell-market space-y-4">
      <Card className="glass">
        <CardContent>
          <h3 className="text-lg font-semibold mb-3">Sell on Market</h3>

          <div className="space-y-3">
            <div>
              <label className="text-sm text-muted-foreground">Select Resource</label>
              <div className="mt-2 space-y-1">
                {ALL_RESOURCES.map((res) => (
                  <button
                    key={res.id}
                    disabled={!res.available}
                    className={`w-full text-left px-3 py-2 rounded border transition-colors ${
                      res.available
                        ? selectedResource?.id === res.id
                          ? 'bg-[#00ff7f]/10 border-[#00ff7f] text-white'
                          : 'border-zinc-700 hover:bg-zinc-800/50 text-white'
                        : 'border-zinc-800 text-zinc-600 cursor-not-allowed'
                    }`}
                    onClick={() => {
                      if (res.available) {
                        setSelectedResource(res)
                        setSaleState({
                          resourceId: res.id,
                          resourceName: res.name,
                          basePrice: 0,
                          units: 0,
                          status: 'setup',
                          marketHistory: [],
                          clusterBids: [],
                          currentRound: 0,
                          roundWinners: [],
                          totalRevenue: 0,
                          avgWinningBid: 0,
                        })
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span>{res.name}</span>
                      {!res.available && <span className="text-xs text-zinc-500">Insufficient level in national reserve</span>}
                      {res.available && res.nationalReserve && (
                        <span className="text-xs text-zinc-400">{res.nationalReserve.toLocaleString()} units</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedResource && saleState && saleState.status === 'setup' && (
        <Card className="glass backdrop-blur-lg bg-white/5 border border-zinc-700">
          <CardContent>
            <h4 className="text-xl font-semibold mb-4">{selectedResource.name} - Market Analysis</h4>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="border border-zinc-700 p-3 rounded">
                <div className="text-xs text-muted-foreground mb-1">6-Month Price Chart</div>
                <div className="h-32 relative bg-black/30 rounded overflow-hidden">
                  <svg className="w-full h-full" preserveAspectRatio="none">
                    {saleState.marketHistory.length > 1 && (
                      <polyline
                        fill="none"
                        stroke="#00ff7f"
                        strokeWidth="2"
                        points={saleState.marketHistory
                          .map((d, i) => {
                            const x = (i / (saleState.marketHistory.length - 1)) * 100
                            const min = Math.min(...saleState.marketHistory.map((m) => m.price))
                            const max = Math.max(...saleState.marketHistory.map((m) => m.price))
                            const y = 100 - ((d.price - min) / (max - min)) * 100
                            return `${x},${y}`
                          })
                          .join(' ')}
                      />
                    )}
                  </svg>
                </div>
              </div>

              <div className="border border-zinc-700 p-3 rounded">
                <div className="text-xs text-muted-foreground mb-2">Average Unit Sale Price</div>
                <div className="text-3xl font-bold text-[#00ff7f]">
                  {saleState.marketHistory.length > 0
                    ? fmt.format(
                        saleState.marketHistory.reduce((s, d) => s + d.price, 0) / saleState.marketHistory.length
                      )
                    : '$0.00'}
                </div>
              </div>
            </div>

            <div className="border border-zinc-700 p-3 rounded mb-4">
              <div className="text-xs text-muted-foreground mb-2">Major Exporters Leaderboard</div>
              <div className="space-y-2">
                {MAJOR_EXPORTERS.map((exp, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="text-zinc-500">#{i + 1}</div>
                      <div className="font-medium">{exp.country}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-zinc-400">{exp.units.toLocaleString()} units</div>
                      <div className="text-[#00ff7f] text-xs">{exp.trend}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm text-white mb-1 block">Base Price (USD/unit)</label>
                <input
                  type="number"
                  className="input w-full px-3 py-2 bg-transparent border-zinc-700 text-white"
                  value={basePrice}
                  onChange={(e) => setBasePrice(Number(e.target.value))}
                  step="0.01"
                  min="0"
                />
              </div>
              <div>
                <label className="text-sm text-white mb-1 block">Number of Units</label>
                <input
                  type="number"
                  className="input w-full px-3 py-2 bg-transparent border-zinc-700 text-white"
                  value={units}
                  onChange={(e) => setUnits(Number(e.target.value))}
                  min="1"
                  max={selectedResource.nationalReserve}
                />
              </div>
            </div>

            <button
              className="btn w-full bg-[#00ff7f] text-black hover:bg-[#00ff7f]/90 font-semibold py-3"
              onClick={startSale}
              disabled={basePrice <= 0 || units <= 0}
            >
              Open to Bids
            </button>
          </CardContent>
        </Card>
      )}

      {saleState && saleState.status === 'verifying' && (
        <Card className="glass backdrop-blur-lg bg-black/80 border border-[#00ff7f]">
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 space-y-8">
              <div className="relative w-24 h-24">
                <div className="absolute inset-0 border-4 border-[#00ff7f]/20 rounded-full animate-ping"></div>
                <div className="absolute inset-0 border-4 border-t-[#00ff7f] rounded-full animate-spin"></div>
              </div>

              <div className="text-center space-y-2">
                <div className="text-2xl font-bold text-[#00ff7f]">{loadingSteps[loadingStep]}</div>
                <div className="text-sm text-zinc-400">Preparing auction environment...</div>
              </div>

              <div className="flex gap-2">
                {loadingSteps.map((_, i) => (
                  <div
                    key={i}
                    className={`h-1 w-16 rounded-full transition-all ${
                      i <= loadingStep ? 'bg-[#00ff7f]' : 'bg-zinc-700'
                    }`}
                  ></div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {saleState && saleState.status === 'live' && (
        <Card className="glass backdrop-blur-lg bg-black/90 border border-[#00ff7f]">
          <CardContent>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h4 className="text-2xl font-bold text-[#00ff7f]">Live Auction - {saleState.resourceName}</h4>
                <div className="text-sm text-zinc-400">
                  Base: {fmt.format(saleState.basePrice)} • {saleState.units.toLocaleString()} units • Round {saleState.currentRound} of {MAX_ROUNDS}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-500 animate-pulse"></div>
                <div className="text-sm font-semibold text-white">LIVE</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {saleState.clusterBids.map((cluster) => {
                const allHighestBids = saleState.clusterBids.map((c) => c.highestBid)
                const globalMax = Math.max(...allHighestBids)
                const globalMin = Math.min(...allHighestBids)
                const range = globalMax - globalMin

                return (
                  <div
                    key={cluster.clusterId}
                    className="border border-[#00ff7f]/30 bg-black/50 p-4 rounded relative overflow-hidden"
                    style={{
                      boxShadow: cluster.highestBid === globalMax && cluster.bidsSubmitted === cluster.totalCountries ? '0 0 20px rgba(0,255,127,0.3)' : 'none',
                    }}
                  >
                    <div className="absolute top-0 left-0 right-0 h-1 bg-zinc-800 overflow-hidden">
                      <div
                        className="h-full bg-[#00ff7f] transition-all duration-300"
                        style={{
                          width: `${(cluster.totalCountries ?? 0) > 0 ? ((cluster.bidsSubmitted ?? 0) / (cluster.totalCountries ?? 1)) * 100 : 0}%`,
                        }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-zinc-500">CLUSTER {cluster.clusterId}</div>
                      <div className="text-[10px] text-zinc-400">
                        {cluster.bidsSubmitted ?? 0}/{cluster.totalCountries ?? 0} in
                      </div>
                    </div>
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                      {cluster.countryBids
                        .filter((bid) => !bid.droppedOut && bid.bidSubmitted)
                        .map((bid, _idx) => ({ ...bid, originalIdx: bid.countryId }))
                        .sort((a, b) => b.amount - a.amount)
                        .map((bid, _rank) => {
                          const isLeading = bid.originalIdx === cluster.leadingCountry
                          const normalized = range > 0 ? (bid.amount - globalMin) / range : 0.5
                          const fontSize = 0.65 + normalized * 0.4
                          
                          return (
                            <div
                              key={bid.originalIdx}
                              className={`transition-all duration-300 ${
                                isLeading ? 'text-[#00ff7f] font-bold' : 'text-zinc-400'
                              }`}
                              style={{ fontSize: `${fontSize}rem` }}
                            >
                              <div className="flex items-center justify-between gap-2">
                                <div className="text-xs truncate">{bid.countryName}</div>
                                <div className="whitespace-nowrap">{fmt.format(bid.amount)}</div>
                              </div>
                            </div>
                          )
                        })}
                      {cluster.countryBids.filter((b) => b.droppedOut).length > 0 && (
                        <div className="text-xs text-red-500/50 italic mt-2">
                          {cluster.countryBids.filter((b) => b.droppedOut).length} withdrew
                        </div>
                      )}
                      {((cluster.bidsSubmitted ?? 0) < (cluster.totalCountries ?? 0)) && (
                        <div className="text-xs text-zinc-600 italic mt-2">
                          Waiting for {((cluster.totalCountries ?? 0) - (cluster.bidsSubmitted ?? 0))} bids...
                        </div>
                      )}
                    </div>
                    {cluster.highestBid === globalMax && ((cluster.bidsSubmitted ?? 0) === (cluster.totalCountries ?? 0)) && (
                      <div className="absolute top-2 right-2">
                        <div className="text-xs font-bold text-[#00ff7f] bg-[#00ff7f]/20 px-2 py-1 rounded">
                          LEADING
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            <div className="mt-6 pt-4 border-t border-zinc-700">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-sm text-zinc-400">Global Highest Bid</div>
                  <div className="text-2xl font-bold text-[#00ff7f]">
                    {fmt.format(Math.max(...saleState.clusterBids.map((c) => c.highestBid)))}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-zinc-400">Total Revenue (So Far)</div>
                  <div className="text-xl font-semibold text-white">
                    {fmt.format(saleState.totalRevenue)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-zinc-400">Avg Winning Bid</div>
                  <div className="text-xl font-semibold text-white">
                    {fmt.format(saleState.avgWinningBid)}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-zinc-800">
                <div className="text-sm text-zinc-400 mb-2">Cluster Competition Index</div>
                <div className="space-y-2">
                  {saleState.clusterBids
                    .map((c, idx) => ({ ...c, originalIdx: idx }))
                    .sort((a, b) => b.highestBid - a.highestBid)
                    .map((cluster, rank) => {
                      const maxBid = Math.max(...saleState.clusterBids.map((c) => c.highestBid))
                      const widthPercent = maxBid > 0 ? (cluster.highestBid / maxBid) * 100 : 0
                      const activeBids = cluster.countryBids.filter((b) => !b.droppedOut).length
                      
                      return (
                        <div key={cluster.clusterId} className="flex items-center gap-2">
                          <div className="text-xs text-zinc-500 w-16">C{cluster.clusterId}</div>
                          <div className="flex-1 bg-zinc-900 rounded-full h-5 relative overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-[#00ff7f]/20 to-[#00ff7f] transition-all duration-500"
                              style={{ width: `${widthPercent}%` }}
                            ></div>
                            <div className="absolute inset-0 flex items-center justify-between px-2">
                              <span className="text-[10px] text-white font-semibold">{fmt.format(cluster.highestBid)}</span>
                              <span className="text-[10px] text-zinc-400">{activeBids} active</span>
                            </div>
                          </div>
                          <div className="text-xs text-zinc-500 w-8">#{rank + 1}</div>
                        </div>
                      )
                    })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {saleState && saleState.status === 'completed' && (
        <Card className="glass backdrop-blur-lg bg-black/90 border border-[#00ff7f]">
          <CardContent>
            <div className="mb-6">
              <h4 className="text-3xl font-bold text-[#00ff7f] mb-2">Auction Complete - {saleState.resourceName}</h4>
              <div className="text-zinc-400">All {MAX_ROUNDS} rounds completed • Final settlement below</div>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-6">
              <div className="bg-zinc-900/50 p-4 rounded border border-[#00ff7f]/30">
                <div className="text-sm text-zinc-400 mb-1">Total Revenue Generated</div>
                <div className="text-3xl font-bold text-[#00ff7f]">{fmt.format(saleState.totalRevenue)}</div>
              </div>
              <div className="bg-zinc-900/50 p-4 rounded border border-zinc-700">
                <div className="text-sm text-zinc-400 mb-1">Average Winning Bid</div>
                <div className="text-2xl font-semibold text-white">{fmt.format(saleState.avgWinningBid)}</div>
              </div>
              <div className="bg-zinc-900/50 p-4 rounded border border-zinc-700">
                <div className="text-sm text-zinc-400 mb-1">Total Units Sold</div>
                <div className="text-2xl font-semibold text-white">{(saleState.units * MAX_ROUNDS).toLocaleString()}</div>
              </div>
            </div>

            <div className="mb-6">
              <h5 className="text-lg font-semibold text-white mb-3">Round-by-Round Performance</h5>
              <div className="space-y-2">
                {Array.from({ length: MAX_ROUNDS }, (_, i) => i + 1).map((round) => {
                  const roundWinners = saleState.roundWinners.filter((w) => w.round === round)
                  const roundRevenue = roundWinners.reduce((sum, w) => sum + w.winningBid, 0)
                  const avgRoundBid = roundWinners.length > 0 ? roundRevenue / roundWinners.length : 0
                  const maxRoundRev = Math.max(
                    ...Array.from({ length: MAX_ROUNDS }, (_, i) => i + 1).map((r) => {
                      const rw = saleState.roundWinners.filter((w) => w.round === r)
                      return rw.reduce((sum, w) => sum + w.winningBid, 0)
                    })
                  )
                  const intensity = maxRoundRev > 0 ? (roundRevenue / maxRoundRev) * 100 : 0

                  return (
                    <div key={round} className="bg-zinc-900/30 p-3 rounded border border-zinc-800 relative overflow-hidden">
                      <div
                        className="absolute inset-0 bg-[#00ff7f]/5 transition-all"
                        style={{ width: `${intensity}%` }}
                      ></div>
                      <div className="relative flex items-center justify-between">
                        <div className="font-semibold text-white">Round {round}</div>
                        <div className="flex items-center gap-4">
                          <div className="text-sm text-zinc-400">
                            Revenue: <span className="text-[#00ff7f] font-semibold">{fmt.format(roundRevenue)}</span>
                          </div>
                          <div className="text-sm text-zinc-400">
                            Avg Bid: <span className="text-white font-semibold">{fmt.format(avgRoundBid)}</span>
                          </div>
                          <div className="text-xs text-[#00ff7f]">{intensity.toFixed(0)}%</div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="mb-6">
              <h5 className="text-lg font-semibold text-white mb-3">Cluster Performance Breakdown</h5>
              <div className="grid grid-cols-3 gap-3">
                {Array.from({ length: 6 }, (_, i) => i + 1).map((clusterId) => {
                  const clusterWins = saleState.roundWinners.filter((w) => w.clusterId === clusterId)
                  const clusterRevenue = clusterWins.reduce((sum, w) => sum + w.winningBid, 0)
                  const clusterAvg = clusterWins.length > 0 ? clusterRevenue / clusterWins.length : 0

                  return (
                    <div key={clusterId} className="bg-zinc-900/50 p-4 rounded border border-zinc-700">
                      <div className="text-xs text-zinc-500 mb-2">CLUSTER {clusterId}</div>
                      <div className="text-xl font-bold text-[#00ff7f] mb-1">{fmt.format(clusterRevenue)}</div>
                      <div className="text-xs text-zinc-400">Avg: {fmt.format(clusterAvg)}</div>
                      <div className="text-xs text-zinc-500 mt-1">{clusterWins.length} rounds won</div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div>
              <h5 className="text-lg font-semibold text-white mb-3">Revenue Distribution</h5>
              <div className="bg-zinc-900/30 p-4 rounded border border-zinc-800">
                <div className="flex items-end justify-between h-32 gap-2">
                  {Array.from({ length: MAX_ROUNDS }, (_, i) => i + 1).map((round) => {
                    const roundWinners = saleState.roundWinners.filter((w) => w.round === round)
                    const roundRevenue = roundWinners.reduce((sum, w) => sum + w.winningBid, 0)
                    const maxRevenue = Math.max(
                      ...Array.from({ length: MAX_ROUNDS }, (_, i) => i + 1).map((r) => {
                        const rw = saleState.roundWinners.filter((w) => w.round === r)
                        return rw.reduce((sum, w) => sum + w.winningBid, 0)
                      })
                    )
                    const heightPercent = maxRevenue > 0 ? (roundRevenue / maxRevenue) * 100 : 0

                    return (
                      <div key={round} className="flex-1 flex flex-col items-center">
                        <div
                          className="w-full bg-[#00ff7f] rounded-t transition-all duration-500"
                          style={{ height: `${heightPercent}%` }}
                        ></div>
                        <div className="text-xs text-zinc-400 mt-2">R{round}</div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                className="flex-1 px-4 py-2 bg-[#00ff7f] text-black font-semibold rounded hover:bg-[#00ff7f]/80 transition-colors"
                onClick={() => setSaleState(null)}
              >
                Close
              </button>
              <button
                className="px-4 py-2 border border-[#00ff7f] text-[#00ff7f] font-semibold rounded hover:bg-[#00ff7f]/10 transition-colors"
                onClick={() => {
                  const doc = document.createElement('div')
                  doc.style.cssText = 'position:absolute;left:-9999px;top:0;width:800px;padding:40px;background:#000;color:#fff;font-family:monospace'
                  
                  doc.innerHTML = `
                    <div style="text-align:center;margin-bottom:30px">
                      <h1 style="color:#00ff7f;font-size:32px;margin-bottom:10px">AUCTION SUMMARY</h1>
                      <h2 style="font-size:24px;margin-bottom:5px">${saleState.resourceName}</h2>
                      <p style="color:#888;font-size:14px">${new Date().toLocaleString()}</p>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:30px">
                      <div style="border:1px solid #00ff7f;padding:15px;border-radius:8px">
                        <div style="color:#888;font-size:12px">TOTAL REVENUE</div>
                        <div style="color:#00ff7f;font-size:24px;font-weight:bold">${fmt.format(saleState.totalRevenue)}</div>
                      </div>
                      <div style="border:1px solid #444;padding:15px;border-radius:8px">
                        <div style="color:#888;font-size:12px">AVG WINNING BID</div>
                        <div style="font-size:20px;font-weight:bold">${fmt.format(saleState.avgWinningBid)}</div>
                      </div>
                      <div style="border:1px solid #444;padding:15px;border-radius:8px">
                        <div style="color:#888;font-size:12px">UNITS SOLD</div>
                        <div style="font-size:20px;font-weight:bold">${(saleState.units * MAX_ROUNDS).toLocaleString()}</div>
                      </div>
                    </div>
                    
                    <div style="margin-bottom:30px">
                      <h3 style="color:#00ff7f;font-size:18px;margin-bottom:15px">Round Performance</h3>
                      ${Array.from({ length: MAX_ROUNDS }, (_, i) => i + 1).map((round) => {
                        const roundWinners = saleState.roundWinners.filter((w) => w.round === round)
                        const roundRevenue = roundWinners.reduce((sum, w) => sum + w.winningBid, 0)
                        const avgRoundBid = roundWinners.length > 0 ? roundRevenue / roundWinners.length : 0
                        return `
                          <div style="background:#111;padding:12px;margin-bottom:8px;border-radius:4px">
                            <span style="font-weight:bold">Round ${round}</span>
                            <span style="float:right">Revenue: <span style="color:#00ff7f">${fmt.format(roundRevenue)}</span> | Avg: ${fmt.format(avgRoundBid)}</span>
                          </div>
                        `
                      }).join('')}
                    </div>
                    
                    <div style="margin-bottom:30px">
                      <h3 style="color:#00ff7f;font-size:18px;margin-bottom:15px">Cluster Breakdown</h3>
                      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px">
                        ${Array.from({ length: 6 }, (_, i) => i + 1).map((clusterId) => {
                          const clusterWins = saleState.roundWinners.filter((w) => w.clusterId === clusterId)
                          const clusterRevenue = clusterWins.reduce((sum, w) => sum + w.winningBid, 0)
                          const clusterAvg = clusterWins.length > 0 ? clusterRevenue / clusterWins.length : 0
                          return `
                            <div style="border:1px solid #444;padding:12px;border-radius:4px">
                              <div style="color:#888;font-size:11px">CLUSTER ${clusterId}</div>
                              <div style="color:#00ff7f;font-size:18px;font-weight:bold;margin:5px 0">${fmt.format(clusterRevenue)}</div>
                              <div style="color:#888;font-size:11px">Avg: ${fmt.format(clusterAvg)}</div>
                              <div style="color:#666;font-size:10px;margin-top:3px">${clusterWins.length} rounds won</div>
                            </div>
                          `
                        }).join('')}
                      </div>
                    </div>
                    
                    <div style="text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid #333">
                      <p style="color:#888;font-size:12px">Generated by NH25 Flux Atlas Trading Platform</p>
                    </div>
                  `
                  
                  document.body.appendChild(doc)
                  
                  setTimeout(() => {
                    window.print()
                    document.body.removeChild(doc)
                    toast.push({ title: 'Export Ready', description: 'Print dialog opened - save as PDF', level: 'success', timeout: 3000 })
                  }, 100)
                }}
              >
                Export PDF
              </button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
