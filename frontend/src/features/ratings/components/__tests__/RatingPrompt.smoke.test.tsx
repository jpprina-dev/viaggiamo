import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RatingPrompt } from '../RatingPrompt'

vi.mock('../../hooks/useSubmitRating', () => ({
  useSubmitRating: () => ({
    mutate: vi.fn(),
    loading: false,
    error: null,
    clearError: vi.fn(),
  }),
}))

describe('RatingPrompt', () => {
  it('renders star picker when no existing rating', () => {
    render(
      <RatingPrompt bookingId={1} rateeId={2} rateeName="Carlos" existingRating={null} />,
    )
    expect(screen.getByText('Calificar a Carlos')).toBeInTheDocument()
  })

  it('renders read-only star display when existingRating is set', () => {
    render(
      <RatingPrompt bookingId={1} rateeId={2} rateeName="Carlos" existingRating={4} />,
    )
    expect(screen.getByText(/Tu calificación a Carlos/)).toBeInTheDocument()
    // Should not show the "Calificar a" prompt
    expect(screen.queryByText('Calificar a Carlos')).not.toBeInTheDocument()
  })
})
