import { useState, useCallback } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import { messageSchema, type Message } from '../types'

const SEND_MESSAGE = gql`
  mutation SendMessage($threadId: Int!, $body: String!) {
    sendMessage(threadId: $threadId, body: $body) {
      id
      threadId
      kind
      senderId
      eventType
      body
      createdAt
    }
  }
`

export interface UseSendMessageResult {
  sendMessage: (threadId: number, body: string) => Promise<Message>
  loading: boolean
  error: string | null
  clearError: () => void
}

function extractErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response: { errors?: Array<{ extensions?: { code?: string } }> } }).response
    const code = response?.errors?.[0]?.extensions?.code
    if (code === 'FORBIDDEN')     return 'No tienes permiso para enviar mensajes en este hilo.'
    if (code === 'UNPROCESSABLE') return 'El chat está cerrado.'
  }
  return 'Error de conexión. Intenta de nuevo.'
}

export function useSendMessage(): UseSendMessageResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (threadId: number, body: string): Promise<Message> => {
    setLoading(true)
    setError(null)
    try {
      const response = await graphqlClient.request<{ sendMessage: unknown }>(SEND_MESSAGE, {
        threadId,
        body,
      })
      return messageSchema.parse(response.sendMessage)
    } catch (err) {
      setError(extractErrorMessage(err))
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { sendMessage, loading, error, clearError: () => setError(null) }
}
