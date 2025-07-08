import type { Metadata } from 'next'
import { DM_Mono, Geist } from 'next/font/google'
import { NuqsAdapter } from 'nuqs/adapters/next/app'
import { Toaster } from '@/components/ui/sonner'
import HydrationProvider from '@/components/HydrationProvider'
import './globals.css'

const geistSans = Geist({
  variable: '--font-geist-sans',
  weight: '400',
  subsets: ['latin']
})

const dmMono = DM_Mono({
  subsets: ['latin'],
  variable: '--font-dm-mono',
  weight: '400'
})

export const metadata: Metadata = {
  title: 'Crypto Research UI - Powered by Salt Wallet',
  description:
    'A modern chat interface for AI-powered crypto market research with real-time web scraping capabilities.'
}

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${dmMono.variable} antialiased`} suppressHydrationWarning>
        <HydrationProvider>
          <NuqsAdapter>{children}</NuqsAdapter>
        </HydrationProvider>
        <Toaster />
      </body>
    </html>
  )
}
