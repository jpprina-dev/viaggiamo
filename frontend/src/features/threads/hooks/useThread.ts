import { useState, useEffect, useCallback, useRef } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import { threadSchema, type Thread } from '../types'
import { MARK_THREAD_READ } from './useMarkThreadRead'

const GET_THREAD = gql`
  query Thread($tripId: Int!, $passengerUserId: Int!) {
    thread(tripId: $tripId, passengerUserId: $passengerUserId) {
      id
      tripId
      passengerUserId
      createdAt
      isClosed
    }
  }
`

export interface UseThreadResult {
  thread: Thread | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useThread(tripId: number, passengerUserId: number): UseThreadResult {
  const [thread, setThread] = useState<Thread | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const markedReadRef = useRef(false)

  const markRead = useCallback(async (threadId: number) => {
    if (markedReadRef.current) return
    markedReadRef.current = true
    try {
      await graphqlClient.request(MARK_THREAD_READ, { threadId })
    } catch {
      // Marking as read is best-effort; reset so a later fetch can retry.
      markedReadRef.current = false
    }
  }, [])

  const fetchThread = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await graphqlClient.request<{ thread: unknown }>(GET_THREAD, {
        tripId,
        passengerUserId,
      })
      if (response.thread === null || response.thread === undefined) {
        setThread(null)
      } else {
        const parsed = threadSchema.parse(response.thread)
        setThread(parsed)
        void markRead(parsed.id)
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch thread'))
      setThread(null)
    } finally {
      setLoading(false)
    }
  }, [tripId, passengerUserId, markRead])

  useEffect(() => {
    fetchThread()
  }, [fetchThread])

  return { thread, loading, error, refetch: fetchThread }
}
