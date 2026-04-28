'use client'

import { useState } from 'react'
import { Star } from 'lucide-react'
import { useSubmitRating } from '../hooks/useSubmitRating'

interface RatingPromptProps {
  bookingId: number
  rateeId: number
  rateeName: string
  existingRating: number | null
}

export function RatingPrompt({ bookingId, rateeName, existingRating }: RatingPromptProps) {
  const [score, setScore] = useState<number>(0)
  const [hovered, setHovered] = useState<number>(0)
  const [comment, setComment] = useState('')
  const [submitted, setSubmitted] = useState(existingRating !== null)
  const { mutate, loading, error } = useSubmitRating()

  // Read-only display
  if (submitted || existingRating !== null) {
    const displayScore = existingRating ?? score
    return (
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Tu calificación a {rateeName}:</span>
        <div className="flex">
          {[1, 2, 3, 4, 5].map((s) => (
            <Star
              key={s}
              className={`w-4 h-4 ${s <= displayScore ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
            />
          ))}
        </div>
      </div>
    )
  }

  const handleSubmit = async () => {
    if (score < 1) return
    try {
      await mutate(bookingId, score, comment || undefined)
      setSubmitted(true)
    } catch {
      // error is already set in hook
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500">Calificar a {rateeName}</p>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((s) => (
          <button
            key={s}
            type="button"
            disabled={loading}
            onMouseEnter={() => setHovered(s)}
            onMouseLeave={() => setHovered(0)}
            onClick={() => setScore(s)}
            className="p-0.5 transition-colors"
          >
            <Star
              className={`w-5 h-5 ${
                s <= (hovered || score)
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
      {score > 0 && (
        <>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Comentario (opcional)"
            rows={2}
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <button
            type="button"
            disabled={loading}
            onClick={() => void handleSubmit()}
            className="px-3 py-1.5 text-xs font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Enviando...' : 'Enviar calificación'}
          </button>
        </>
      )}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}
