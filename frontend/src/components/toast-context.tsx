import { createContext } from 'react'

export type ToastLevel = 'info' | 'success' | 'error'

export type ToastItem = {
  id: string
  title: string
  description?: string
  level?: ToastLevel
  timeout?: number
  isConfirm?: boolean
  resolve?: (v: boolean) => void
}

export type ToastContextValue = {
  push: (t: Omit<ToastItem, 'id'>) => string
  showConfirm: (t: { title: string; description?: string }) => Promise<boolean>
}

export const ToastContext = createContext<ToastContextValue | null>(null)
