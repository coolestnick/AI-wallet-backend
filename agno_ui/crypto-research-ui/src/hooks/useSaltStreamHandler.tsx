import { useCallback } from 'react'
import { streamSaltChatAPI } from '@/api/salt-adapter'
import useChatActions from '@/hooks/useChatActions'
import { usePlaygroundStore } from '../store'
import { RunEvent } from '@/types/playground'
import { useQueryState } from 'nuqs'
import { getTimestamp, getTimestampWithOffset } from '@/lib/timestamp'

/**
 * Custom hook for handling Salt Wallet streaming API
 */
const useSaltStreamHandler = () => {
  const setMessages = usePlaygroundStore((state) => state.setMessages)
  const { addMessage, focusChatInput } = useChatActions()
  const [agentId] = useQueryState('agent')
  const [sessionId, setSessionId] = useQueryState('session')
  const selectedEndpoint = usePlaygroundStore((state) => state.selectedEndpoint)
  const setStreamingErrorMessage = usePlaygroundStore(
    (state) => state.setStreamingErrorMessage
  )
  const setIsStreaming = usePlaygroundStore((state) => state.setIsStreaming)

  const updateMessagesWithErrorState = useCallback(() => {
    setMessages((prevMessages) => {
      const newMessages = [...prevMessages]
      const lastMessage = newMessages[newMessages.length - 1]
      if (lastMessage && lastMessage.role === 'agent') {
        lastMessage.streamingError = true
      }
      return newMessages
    })
  }, [setMessages])

  const handleSaltStreamResponse = useCallback(
    async (input: string | FormData) => {
      if (!agentId) return
      
      setIsStreaming(true)
      
      const message = input instanceof FormData ? input.get('message') as string : input
      
      // Remove previous error messages
      setMessages((prevMessages) => {
        if (prevMessages.length >= 2) {
          const lastMessage = prevMessages[prevMessages.length - 1]
          const secondLastMessage = prevMessages[prevMessages.length - 2]
          if (
            lastMessage.role === 'agent' &&
            lastMessage.streamingError &&
            secondLastMessage.role === 'user'
          ) {
            return prevMessages.slice(0, -2)
          }
        }
        return prevMessages
      })

      // Add user message
      addMessage({
        role: 'user',
        content: message,
        created_at: getTimestamp()
      })

      // Add initial agent message
      addMessage({
        role: 'agent',
        content: '',
        tool_calls: [],
        streamingError: false,
        created_at: getTimestampWithOffset(1)
      })

      // Convert previous messages to Salt Wallet format
      const messages = usePlaygroundStore.getState().messages
      const saltMessages = messages
        .filter(msg => msg.role === 'user' || msg.role === 'agent')
        .map(msg => ({
          role: msg.role === 'agent' ? 'assistant' : msg.role,
          content: msg.content
        }))

      // Add the new user message
      saltMessages.push({ role: 'user', content: message })

      try {
        await streamSaltChatAPI(
          selectedEndpoint,
          agentId,
          saltMessages,
          (chunk) => {
            // Handle streaming chunks
            if (chunk.event === 'RunCompleted') {
              // Final chunk - don't process content
              return
            }
            
            if (chunk.content) {
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages]
                const lastMessage = newMessages[newMessages.length - 1]
                if (lastMessage && lastMessage.role === 'agent') {
                  lastMessage.content += chunk.content
                  lastMessage.created_at = chunk.created_at ?? lastMessage.created_at
                }
                return newMessages
              })
            }
          },
          (error) => {
            // Handle errors
            updateMessagesWithErrorState()
            setStreamingErrorMessage(error)
          },
          () => {
            // Handle completion
            focusChatInput()
            setIsStreaming(false)
          }
        )
      } catch (error) {
        updateMessagesWithErrorState()
        setStreamingErrorMessage(
          error instanceof Error ? error.message : String(error)
        )
        focusChatInput()
        setIsStreaming(false)
      }
    },
    [
      setMessages,
      addMessage,
      updateMessagesWithErrorState,
      selectedEndpoint,
      agentId,
      setStreamingErrorMessage,
      setIsStreaming,
      focusChatInput
    ]
  )

  return { handleSaltStreamResponse }
}

export default useSaltStreamHandler