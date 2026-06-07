import { useState, useEffect, useCallback, useRef } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import { messageSchema, type Message } from '../types'

const POLL_INTERVAL_MS = 5000

const GET_MESSAGES = gql`
  query Messages($threadId: Int!) {
    messages(threadId: $threadId) {
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

export interface UseThreadPollingResult {
  messages: Message[]
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useThreadPolling(threadId: number | null): UseThreadPollingResult {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchMessages = useCallback(async () => {
    if (threadId === null) return
    try {
      const response = await graphqlClient.request<{ messages: unknown[] }>(GET_MESSAGES, {
        threadId,
      })
      const parsed = response.messages.map((m) => messageSchema.parse(m))
      setMessages(parsed)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch messages'))
    } finally {
      setLoading(false)
    }
  }, [threadId])

  useEffect(() => {
    if (threadId === null) {
      setLoading(false)
      return
    }

    setLoading(true)
    fetchMessages()

    intervalRef.current = setInterval(() => {
      fetchMessages()
    }, POLL_INTERVAL_MS)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [threadId, fetchMessages])

  return { messages, loading, error, refetch: fetchMessages }
}
