import { Agent, ComboboxAgent } from '@/types/playground'

// Adapter to transform Salt Wallet API responses to Agno UI format
export const getSaltAgentsAPI = async (
  endpoint: string
): Promise<ComboboxAgent[]> => {
  try {
    const response = await fetch(`${endpoint}/api/v1/agents`, { method: 'GET' })
    if (!response.ok) {
      console.error(`Failed to fetch agents: ${response.statusText}`)
      return []
    }
    const data = await response.json()
    
    // Transform Salt Wallet API response to Agno UI format
    const agents: ComboboxAgent[] = data.agents
      .filter((agent: any) => agent.agent_id.includes('_')) // Only original agent IDs
      .map((agent: any) => ({
        value: agent.agent_id,
        label: agent.name,
        model: {
          provider: 'Salt Wallet',
          name: 'Gemini',
          model: 'gemini-2.0-flash-lite'
        },
        storage: false
      }))
    
    return agents
  } catch (error) {
    console.error('Error fetching Salt Wallet agents:', error)
    return []
  }
}

export const getSaltStatusAPI = async (base: string): Promise<number> => {
  try {
    const response = await fetch(`${base}/health`, { method: 'GET' })
    return response.status
  } catch {
    return 500
  }
}

// Stream chat with Salt Wallet agent
export const streamSaltChatAPI = async (
  endpoint: string,
  agentId: string,
  messages: Array<{ role: string; content: string }>,
  onChunk: (chunk: any) => void,
  onError: (error: string) => void,
  onComplete: () => void
) => {
  try {
    const response = await fetch(`${endpoint}/api/v1/agents/${agentId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        session_id: `session-${Date.now()}`,
        user_id: 'agno-ui-user'
      }),
    })

    if (!response.ok) {
      onError(`HTTP error! status: ${response.status}`)
      return
    }

    const reader = response.body?.getReader()
    if (!reader) {
      onError('No reader available')
      return
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      
      // Process complete lines
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.trim() === '') continue
        
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data.trim() === '') continue
          
          try {
            const parsed = JSON.parse(data)
            
            if (parsed.error) {
              onError(parsed.error)
              return
            }
            
            // Transform to Agno UI format
            const chunk = {
              event: parsed.done ? 'RunCompleted' : 'RunResponse',
              content: parsed.content || '',
              done: parsed.done || false,
              created_at: Date.now()
            }
            
            onChunk(chunk)
            
            if (parsed.done) {
              onComplete()
              return
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }
      }
    }
  } catch (error) {
    onError(`Network error: ${error}`)
  }
}