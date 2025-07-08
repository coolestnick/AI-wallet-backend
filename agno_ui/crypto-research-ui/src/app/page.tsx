'use client'
import Sidebar from '@/components/playground/Sidebar/Sidebar'
import { ChatArea } from '@/components/playground/ChatArea'
import { Suspense } from 'react'

export default function Home() {
  return (
    <Suspense fallback={
      <div className="flex h-screen bg-background/80 items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading components...</p>
        </div>
      </div>
    }>
      <div className="flex h-screen bg-background/80">
        <Sidebar />
        <ChatArea />
      </div>
    </Suspense>
  )
}
