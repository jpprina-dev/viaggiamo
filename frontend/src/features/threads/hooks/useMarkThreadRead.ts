import { useState } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'

const MARK_THREAD_READ = gql`
  mutation MarkThreadRead($threadId: Int!) {
    markThreadRead(threadId: $threadId)
  }
`

export interface UseMarkThreadReadResult {
  markThreadRead: (threadId: number) => Promise<void>
  loading: boolean
  error: string | null
  clearError: () => void
}

export function useMarkThreadRead(): UseMarkThreadReadResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const markThreadRead = async (threadId: number): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      await graphqlClient.request(MARK_THREAD_READ, { threadId })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'No se pudo marcar como leído.'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { markThreadRead, loading, error, clearError: () => setError(null) }
}
