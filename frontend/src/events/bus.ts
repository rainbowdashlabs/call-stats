// Simple global event bus for the app
// Provides on/off/emit and a helper emitError to standardize error events

export type EventHandler<T = any> = (payload: T) => void

class EventBus {
  private listeners: Map<string, Set<EventHandler>> = new Map()

  on<T = any>(event: string, handler: EventHandler<T>): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(handler as EventHandler)
    return () => this.off(event, handler as EventHandler)
  }

  off(event: string, handler: EventHandler) {
    this.listeners.get(event)?.delete(handler)
  }

  emit<T = any>(event: string, payload: T) {
    this.listeners.get(event)?.forEach(h => {
      try { h(payload) } catch (e) { /* swallow */ }
    })
  }
}

export const bus = new EventBus()

export type ErrorEventPayload = {
  message: string
  code?: string | number
  details?: any
}

// Normalize various error shapes (AxiosError / Fetch / generic Error / string)
export function emitError(err: unknown, extra?: Partial<ErrorEventPayload>) {
  let payload: ErrorEventPayload = { message: 'An unexpected error occurred.' }

  // Try to detect Axios-like error
  const anyErr: any = err as any
  if (anyErr) {
    // axios v1: isAxiosError flag and response structure
    const resp = anyErr.response
    const data = resp?.data
    const msg = data?.message || data?.error || anyErr.message || String(anyErr)
    payload = {
      message: msg ?? payload.message,
      code: resp?.status || anyErr.code,
      details: data ?? anyErr
    }
  }

  if (extra) payload = { ...payload, ...extra }

  bus.emit<ErrorEventPayload>('error', payload)
}
