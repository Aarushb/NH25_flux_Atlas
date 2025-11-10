import React, { createContext, useState } from 'react'

type ToastLevel = 'info' | 'success' | 'error'

type ToastItem = {
  id: string
  title: string
  description?: string
  level?: ToastLevel
  timeout?: number
  isConfirm?: boolean
  resolve?: (v: boolean) => void
}

type ToastContextValue = {
  push: (t: Omit<ToastItem, 'id'>) => string
  showConfirm: (t: { title: string; description?: string }) => Promise<boolean>
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const push = (t: Omit<ToastItem, 'id'>) => {
    const id = Math.random().toString(36).slice(2, 9)
    const item: ToastItem = { id, ...t }
    setToasts((s) => [...s, item])
    if (t.timeout && t.timeout > 0) {
      setTimeout(() => setToasts((s) => s.filter((x) => x.id !== id)), t.timeout)
    }
    return id
  }

  const showConfirm = (t: { title: string; description?: string }) =>
    new Promise<boolean>((resolve) => {
      push({ title: t.title, description: t.description, isConfirm: true, resolve })
    })

  const value = { push, showConfirm }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-60 flex flex-col gap-3">
        {toasts.map((t) => (
          <div key={t.id} className={`w-[320px] rounded border px-3 py-2 glass drop-shadow-lg ${t.level === 'error' ? 'border-red-600' : t.level === 'success' ? 'border-green-400' : 'border-zinc-700'}`}>
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-sm font-semibold">{t.title}</div>
                {t.description && <div className="text-xs text-muted-foreground mt-1">{t.description}</div>}
              </div>
              {t.isConfirm ? (
                <div className="flex items-center gap-2">
                  <button
                    className="btn btn-sm opacity-80"
                    onClick={() => {
                      setToasts((s) => s.filter((x) => x.id !== t.id))
                      t.resolve?.(true)
                    }}
                  >
                    Continue
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => {
                      setToasts((s) => s.filter((x) => x.id !== t.id))
                      t.resolve?.(false)
                    }}
                  >
                    Exit
                  </button>
                </div>
              ) : (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setToasts((s) => s.filter((x) => x.id !== t.id))}
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
export default ToastProvider
