import { z } from 'zod'

export interface Rating {
  id: number
  bookingId: number
  raterId: number
  rateeId: number
  score: number
  comment: string | null
}

export const ratingSchema = z.object({
  id: z.number(),
  bookingId: z.number(),
  raterId: z.number(),
  rateeId: z.number(),
  score: z.number().int().min(1).max(5),
  comment: z.string().nullable(),
})
