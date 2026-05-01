import { useCallback, useEffect, useState } from 'react'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/lib/graphql-client'
import type { Rating } from '../types'

const MY_RATINGS_QUERY = gql`
  query MyRatings {
    myRatings {
      id
      bookingId
      raterId
      rateeId
      score
      comment
    }
  }
`

interface UseMyRatingsResult {
  ratings: Rating[]
  loading: boolean
  refetch: () => Promise<void>
}

export function useMyRatings(): UseMyRatingsResult {
  const [ratings, setRatings] = useState<Rating[]>([])
  const [loading, setLoading] = useState(false)

  const fetchRatings = useCallback(async () => {
    setLoading(true)
    try {
      const res = await graphqlClient.request<{ myRatings: Rating[] }>(MY_RATINGS_QUERY)
      setRatings(res.myRatings)
    } catch {
      // non-critical — ratings prompt still works without this
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchRatings() }, [fetchRatings])

  return { ratings, loading, refetch: fetchRatings }
}
