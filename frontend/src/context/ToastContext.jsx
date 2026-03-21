import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

const TOAST_DURATION_MS = 4000

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, TOAST_DURATION_MS)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  )
}

function ToastContainer({ toasts, onClose }) {
  if (toasts.length === 0) return null
  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
      role="region"
      aria-label="Notificações"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          role="alert"
          className={`pointer-events-auto rounded-lg border px-4 py-3 shadow-lg ${
            t.type === 'error'
              ? 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/35 dark:border-red-700 dark:text-red-200'
              : 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/35 dark:border-green-700 dark:text-green-200'
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium">{t.message}</p>
            <button
              type="button"
              onClick={() => onClose(t.id)}
              className="shrink-0 text-current opacity-70 hover:opacity-100 focus:outline-none"
              aria-label="Fechar"
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
