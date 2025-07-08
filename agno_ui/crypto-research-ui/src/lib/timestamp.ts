/**
 * Utility for generating consistent timestamps that work across server and client
 */

let serverTimestamp: number | null = null

export function getTimestamp(): number {
  // On the server, use a fixed timestamp that gets hydrated to the client
  if (typeof window === 'undefined') {
    if (serverTimestamp === null) {
      serverTimestamp = Math.floor(Date.now() / 1000)
    }
    return serverTimestamp
  }
  
  // On the client, use actual current time
  return Math.floor(Date.now() / 1000)
}

export function getTimestampWithOffset(offset: number = 0): number {
  return getTimestamp() + offset
}

// For cases where we need a unique ID but want to avoid hydration issues
export function generateMessageId(): string {
  if (typeof window === 'undefined') {
    // On server, use a predictable ID
    return `msg-${Date.now()}-server`
  }
  // On client, use actual timestamp + random
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}