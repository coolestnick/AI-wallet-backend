import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7777'
  }
}

export default nextConfig
EOF < /dev/null