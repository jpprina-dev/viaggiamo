import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useThreadPolling } from '../useThreadPolling'

vi.mock('@/lib/graphql-client', () => ({
  graphqlClient: { request: vi.fn().mockResolvedValue({ messages: [] }) },
}))

describe('useThreadPolling', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  // Behavior 5
  it('clears the polling interval on unmount', () => {
    const clearSpy = vi.spyOn(globalThis, 'clearInterval')
    const { unmount } = renderHook(() => useThreadPolling(42))
    unmount()
    expect(clearSpy).toHaveBeenCalled()
  })

  it('does not poll when threadId is null', () => {
    const setSpy = vi.spyOn(globalThis, 'setInterval')
    renderHook(() => useThreadPolling(null))
    expect(setSpy).not.toHaveBeenCalled()
  })
})
