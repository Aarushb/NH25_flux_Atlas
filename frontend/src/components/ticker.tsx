import { useEffect, useRef } from 'react'

type Tick = { id: string; resource: string; location: string; price: number; change: number }

const DUMMY: Tick[] = [
  { id: '1', resource: 'Aluminum', location: 'US', price: 2345.5, change: 1.2 },
  { id: '2', resource: 'Oil', location: 'Brent', price: 78.12, change: -6.7 },
  { id: '3', resource: 'Natural Gas', location: 'Henry Hub', price: 3.45, change: 2.3 },
  { id: '4', resource: 'Uranium', location: 'Kazakhstan', price: 72.0, change: -1.1 },
  { id: '5', resource: 'Copper', location: 'Chile', price: 8450.75, change: 0.4 },
]

function countryToFlagEmoji(loc: string) {
  const iso = (loc || '').trim().toUpperCase()
  if (/^[A-Z]{2}$/.test(iso)) {
    const A = 0x1f1e6
    return String.fromCodePoint(...iso.split('').map((c) => A + (c.charCodeAt(0) - 65)))
  }
  const map: Record<string, string> = {
    'UNITED STATES': '🇺🇸', 'US': '🇺🇸', 'BRAZIL': '🇧🇷', 'CHILE': '🇨🇱', 'KAZAKHSTAN': '🇰🇿',
    'UK': '🇬🇧', 'CHINA': '🇨🇳', 'INDIA': '🇮🇳', 'WORLD': '🌐', 'BRENT': '🛢️', 'HENRY HUB': '⛽️',
  }
  const key = loc.trim().toUpperCase()
  return map[key] ?? '🌐'
}

export default function Ticker() {
  const wrapRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {}, [])

  return (
    <div aria-hidden="true" className="fixed left-0 right-0 bottom-0 z-50 bg-[#020608] border-t border-zinc-700 text-sm">
      <div className="max-w-full overflow-hidden ticker-wrap">
        <div ref={wrapRef} className="ticker-track">
          {[0, 1].map((copy) => (
            <div key={copy} className="ticker-seq">
              {DUMMY.map((t) => {
                const flag = countryToFlagEmoji(t.location)
                const positive = t.change >= 0
                const color = positive ? '#00ff7f' : '#ff2d55'
                const bg = positive ? '#00220f' : '#22050a'
                const glow = positive ? '0 0 36px rgba(0,255,127,0.5)' : '0 0 36px rgba(255,45,85,0.4)'
                return (
                  <div key={t.id + '-' + copy} className="ticker-item" style={{ background: bg, border: `2px solid ${color}`, boxShadow: glow, borderRadius: 0 }}>
                    <span style={{ fontSize: 20, marginRight: 6 }} aria-hidden>{flag}</span>
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'rgba(255,255,255,0.95)', marginRight: 8 }}>{t.resource}</span>
                    <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.95)', marginRight: 12 }}>{t.location}</span>
                    <span style={{ fontSize: 18, fontWeight: 800, color, textShadow: `0 0 28px ${color}`, marginRight: 10 }}>${t.price.toFixed(2)}</span>
                    <span style={{ fontSize: 13, fontWeight: 800, color }}>{positive ? '+' : ''}{t.change}%</span>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      <style>{`
@keyframes marquee { 
  0% { transform: translateX(0); } 
  100% { transform: translateX(-50%); } 
}
.ticker-track { display: flex; gap: 0; align-items: center; padding: 0.22rem 0; animation: marquee 8s linear infinite; }
.ticker-wrap:hover .ticker-track { animation-play-state: paused; }
.ticker-seq { display: flex; }
.ticker-item { display: inline-flex; align-items: center; padding: 0.42rem 0.86rem; margin: 0; border-radius: 0; }
      `}</style>
    </div>
  )
}
import { useEffect, useRef } from 'react'

type Tick = {
  id: string
  resource: string
  location: string
  price: number
  change: number
}

const DUMMY: Tick[] = [
  { id: '1', resource: 'Aluminum', location: 'US', price: 2345.5, change: 1.2 },
  { id: '2', resource: 'Oil', location: 'Brent', price: 78.12, change: -6.7 },
  { id: '3', resource: 'Natural Gas', location: 'Henry Hub', price: 3.45, change: 2.3 },
  { id: '4', resource: 'Uranium', location: 'Kazakhstan', price: 72.0, change: -1.1 },
  { id: '5', resource: 'Copper', location: 'Chile', price: 8450.75, change: 0.4 },
]

function countryToFlagEmoji(loc: string) {
  const iso = (loc || '').trim().toUpperCase()
  if (/^[A-Z]{2}$/.test(iso)) {
    const A = 0x1f1e6
    return String.fromCodePoint(...iso.split('').map((c) => A + (c.charCodeAt(0) - 65)))
  }
  const map: Record<string, string> = {
    'UNITED STATES': '🇺🇸',
    'US': '🇺🇸',
    'BRAZIL': '🇧🇷',
    'CHILE': '🇨🇱',
    'KAZAKHSTAN': '🇰🇿',
    'UK': '🇬🇧',
    'CHINA': '🇨🇳',
    'INDIA': '🇮🇳',
    'WORLD': '🌐',
    'BRENT': '🛢️',
    'HENRY HUB': '⛽️',
  }
  const key = loc.trim().toUpperCase()
  return map[key] ?? '🌐'
}

export default function Ticker() {
  const wrapRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const css = `
@keyframes marquee { 
  0% { transform: translateX(0); } 
  100% { transform: translateX(-50%); } 
}
.ticker-track { display: flex; gap: 0; align-items: center; padding: 0.22rem 0; animation: marquee 8s linear infinite; }
.ticker-wrap:hover .ticker-track { animation-play-state: paused; }
.ticker-seq { display: flex; }
.ticker-item { display: inline-flex; align-items: center; padding: 0.42rem 0.86rem; margin: 0; border-radius: 0; }
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
          {/* two copies for smooth looping */}
          {[0, 1].map((copy) => (
            <div key={copy} className="ticker-seq">
              {DUMMY.map((t) => {
                const flag = countryToFlagEmoji(t.location)
                const positive = t.change >= 0
                const color = positive ? '#00ff7f' : '#ff2d55'
                const bg = positive ? '#00220f' : '#22050a'
                const glow = positive ? '0 0 28px rgba(0,255,127,0.45)' : '0 0 28px rgba(255,45,85,0.35)'
                return (
                  <div
                    key={t.id + '-' + copy}
                    className="ticker-item"
                    style={{ background: bg, border: `2px solid ${color}`, boxShadow: glow, borderRadius: 0 }}
                  >
                    <span style={{ fontSize: 20, marginRight: 6 }} aria-hidden>
                      {flag}
                    </span>
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'rgba(255,255,255,0.95)', marginRight: 8 }}>{t.resource}</span>
                    <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.95)', marginRight: 12 }}>{t.location}</span>
                    <span style={{ fontSize: 18, fontWeight: 800, color, textShadow: `0 0 22px ${color}`, marginRight: 10 }}>${t.price.toFixed(2)}</span>
                    <span style={{ fontSize: 13, fontWeight: 800, color }}>{positive ? '+' : ''}{t.change}%</span>
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
import { useEffect, useRef } from 'react'

type Tick = {
  id: string
  resource: string
  location: string
  price: number
  change: number
}

const DUMMY: Tick[] = [
  { id: '1', resource: 'Aluminum', location: 'US', price: 2345.5, change: 1.2 },
  { id: '2', resource: 'Oil', location: 'Brent', price: 78.12, change: -6.7 },
  { id: '3', resource: 'Natural Gas', location: 'Henry Hub', price: 3.45, change: 2.3 },
  { id: '4', resource: 'Uranium', location: 'Kazakhstan', price: 72.0, change: -1.1 },
  { id: '5', resource: 'Copper', location: 'Chile', price: 8450.75, change: 0.4 },
]

function countryToFlagEmoji(loc: string) {
  const iso = (loc || '').trim().toUpperCase()
  if (/^[A-Z]{2}$/.test(iso)) {
    const A = 0x1f1e6
    return String.fromCodePoint(...iso.split('').map((c) => A + (c.charCodeAt(0) - 65)))
  }
  const map: Record<string, string> = {
    'UNITED STATES': '🇺🇸',
    'US': '🇺🇸',
    'BRAZIL': '🇧🇷',
    'CHILE': '🇨🇱',
    'KAZAKHSTAN': '🇰🇿',
    'UK': '🇬🇧',
    'BRU': '🇧🇷',
    'CHINA': '🇨🇳',
    'INDIA': '🇮🇳',
    'WORLD': '🌐',
    'BRENT': '🛢️',
    'HENRY HUB': '⛽️',
  }
  const key = loc.trim().toUpperCase()
  return map[key] ?? '🌐'
}

export default function Ticker() {
  const wrapRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
  }, [])

  return (
    <div aria-hidden="true" className="fixed left-0 right-0 bottom-0 z-50 bg-[#020608] border-t border-zinc-700 text-sm">
      <div className="max-w-full overflow-hidden ticker-wrap">
        <div
        <style>{`\
          @keyframes marquee {\n\
            0% { transform: translateX(0); }\n\
            100% { transform: translateX(-50%); }\n+        }\n+\n+        .animate-marquee { animation: marquee 10s linear infinite; animation-play-state: running; }\n+       \n+        .ticker-wrap:hover .animate-marquee { animation-play-state: paused; }\n+        /* remove spacing between blocks and force inline-flex */\n+        .ticker-item { padding-right: 0; margin-right: 0; display: inline-flex; }\n+        .ticker-wrap { cursor: default; }\n+      `}</style>
            <div key={copy} className="flex items-center">
              {DUMMY.map((t) => {
                const flag = countryToFlagEmoji(t.location)
                const positive = t.change >= 0
                const itemStyle: React.CSSProperties = positive
                  ? { backgroundColor: '#00220f', color: '#eaffef', boxShadow: '0 0 28px rgba(0,255,127,0.35)', border: '2px solid rgba(0,255,127,0.5)', padding: '0.45rem 0.9rem', borderRadius: 0, marginRight: 0 }
                  : { backgroundColor: '#22050a', color: '#ffeef2', boxShadow: '0 0 28px rgba(255,45,85,0.28)', border: '2px solid rgba(255,45,85,0.4)', padding: '0.45rem 0.9rem', borderRadius: 0, marginRight: 0 }
                return (
                  <div key={t.id + '-' + copy} className="inline-flex items-center ticker-item" style={itemStyle}>
                    <span className="text-2xl leading-none" style={{ marginRight: 6 }} aria-hidden>
                      {flag}
                    </span>
                    <div className="text-sm uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.95)', fontWeight: 700 }}>{t.resource}</div>
                    <div className="font-semibold" style={{ color: 'rgba(255,255,255,0.98)', marginLeft: 6 }}>{t.location}</div>
                    <div className="font-extrabold text-xl" style={{ color: positive ? '#00ff7f' : '#ff2955', textShadow: '0 0 22px rgba(0,255,127,0.5)' , marginLeft: 10 }}>${t.price.toFixed(2)}</div>
                    <div className="px-2 py-0.5 text-sm" style={{ background: 'transparent', color: positive ? '#00ff7f' : '#ff2d55', marginLeft: 8, fontWeight: 800 }}>
                      {positive ? '+' : ''}{t.change}%
                    </div>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      <style>{`\
        @keyframes marquee {\n\
          0% { transform: translateX(0); }\n\
          100% { transform: translateX(-50%); }\n\
        }\n\
        .animate-marquee { animation: marquee 10s linear infinite; animation-play-state: running; }\n+        /* pause when hovering the ticker area */\n+        .ticker-wrap:hover .animate-marquee { animation-play-state: paused; }\n+        .ticker-item { padding-right: 8px; margin-right: 6px; }\n+        .ticker-wrap { cursor: default; }\n+      `}</style>
    </div>
  )
}