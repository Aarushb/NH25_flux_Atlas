import { useEffect, useRef } from 'react'

type Tick = { id: string; resource: string; location: string; price: number; change: number }

const DUMMY: Tick[] = [
  { id: '1', resource: 'Aluminum', location: 'US', price: 2345.5, change: 1.2 },
  { id: '2', resource: 'Oil', location: 'Brent', price: 78.12, change: -6.7 },
  { id: '3', resource: 'Natural Gas', location: 'Henry Hub', price: 3.45, change: 2.3 },
  { id: '4', resource: 'Uranium', location: 'Kazakhstan', price: 72.0, change: -1.1 },
  { id: '5', resource: 'Copper', location: 'Chile', price: 8450.75, change: 0.4 },
]

function countryToFlagUrl(loc: string) {
  const key = (loc || '').trim().toUpperCase()
  if (/^[A-Z]{2}$/.test(key)) return `/flags/${key.toLowerCase()}.svg`
  const map: Record<string, string> = {
    'UNITED STATES': '/flags/us.svg', 'US': '/flags/us.svg', 'BRAZIL': '/flags/oil.svg', 'CHILE': '/flags/cl.svg', 'KAZAKHSTAN': '/flags/kz.svg',
    'UK': '/flags/world.svg', 'CHINA': '/flags/world.svg', 'INDIA': '/flags/world.svg', 'WORLD': '/flags/world.svg', 'BRENT': '/flags/oil.svg', 'HENRY HUB': '/flags/gas.svg',
  }
  return map[key] ?? '/flags/world.svg'
}

export default function Ticker() {
  const wrapRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const css = `
@keyframes marquee { 
  0% { transform: translateX(0); } 
  100% { transform: translateX(-50%); } 
}
.ticker-track { display: flex; gap: 0; align-items: center; padding: 0.12rem 0; animation: marquee 8s linear infinite; }
.ticker-wrap:hover .ticker-track { animation-play-state: paused; }
.ticker-seq { display: flex; }
.ticker-item { display: inline-flex; align-items: center; padding: 0.18rem 0.5rem; margin: 0; border-radius: 0; }
`
    const el = document.createElement('style')
    el.setAttribute('data-generated', 'ticker-css')
    el.innerHTML = css
    document.head.appendChild(el)
    return () => { document.head.removeChild(el) }
  }, [])

  return (
    <div aria-hidden="true" className="fixed left-0 right-0 bottom-0 z-50 bg-[#020608] border-t border-zinc-700 text-sm">
      <div className="max-w-full overflow-hidden ticker-wrap">
        <div ref={wrapRef} className="ticker-track">
          {[0, 1].map((copy) => (
            <div key={copy} className="ticker-seq">
              {DUMMY.map((t) => {
                const flag = countryToFlagUrl(t.location)
                const positive = t.change >= 0
                const color = positive ? '#00ff7f' : '#ff2d55'
                const bg = positive ? '#00220f' : '#22050a'
                const glow = positive ? '0 0 36px rgba(0,255,127,0.55)' : '0 0 36px rgba(255,45,85,0.45)'
                return (
                  <div key={t.id + '-' + copy} className="ticker-item" style={{ background: bg, border: `2px solid ${color}`, boxShadow: glow, borderRadius: 0 }}>
                    <img src={flag} alt={t.location} style={{ width: 18, height: 12, objectFit: 'cover', marginRight: 6 }} onError={(e) => { (e.target as HTMLImageElement).src = '/flags/world.svg' }} />
                    <span style={{ fontSize: 11, fontWeight: 700, color: 'rgba(255,255,255,0.95)', marginRight: 8 }}>{t.resource}</span>
                    <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.95)', marginRight: 8 }}>{t.location}</span>
                    <span style={{ fontSize: 14, fontWeight: 800, color, textShadow: `0 0 20px ${color}`, marginRight: 10 }}>${t.price.toFixed(2)}</span>
                    <span style={{ fontSize: 11, fontWeight: 800, color }}>{positive ? '+' : ''}{t.change}%</span>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
