'use client'

import { useEffect, useState } from 'react'

interface HydrationProviderProps {
  children: React.ReactNode
}

/**
 * HydrationProvider that ensures proper hydration handling
 * Prevents hydration mismatches caused by browser extensions or server/client differences
 */
export default function HydrationProvider({ children }: HydrationProviderProps) {
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    // Mark as hydrated after the component mounts on the client
    setIsHydrated(true)
  }, [])

  // During server-side rendering and initial client render, 
  // show a loading state to prevent hydration mismatches
  if (!isHydrated) {
    return (
      <div className="flex h-screen bg-background/80 items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Initializing Agno UI...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}