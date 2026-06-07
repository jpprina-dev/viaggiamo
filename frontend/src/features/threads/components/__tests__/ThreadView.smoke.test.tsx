import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThreadView } from '../ThreadView'
import type { Message, Thread } from '../../types'

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1, name: 'Test' } }),
}))

vi.mock('../../hooks/useThread')
vi.mock('../../hooks/useThreadPolling')

import { useThread } from '../../hooks/useThread'
import { useThreadPolling } from '../../hooks/useThreadPolling'

const baseThread: Thread = {
  id: 99,
  tripId: 10,
  passengerUserId: 2,
  createdAt: '2026-06-01T10:00:00',
  isClosed: false,
}

const userMessage: Message = {
  id: 1,
  threadId: 99,
  kind: 'user',
  senderId: 2,
  eventType: null,
  body: 'Hola, ¿a qué hora salís?',
  createdAt: '2026-06-01T10:05:00',
}

const systemMessage: Message = {
  id: 2,
  threadId: 99,
  kind: 'system',
  senderId: null,
  eventType: 'request_sent',
  body: null,
  createdAt: '2026-06-01T10:01:00',
}

beforeEach(() => {
  vi.mocked(useThread).mockReturnValue({ thread: baseThread, loading: false, error: null, refetch: vi.fn() })
  vi.mocked(useThreadPolling).mockReturnValue({ messages: [], loading: false, error: null, refetch: vi.fn() })
})

describe('ThreadView', () => {
  // Behavior 1
  it('renders user messages when received', () => {
    vi.mocked(useThreadPolling).mockReturnValue({ messages: [userMessage], loading: false, error: null, refetch: vi.fn() })
    render(<ThreadView tripId={10} passengerUserId={2} />)
    expect(screen.getByText('Hola, ¿a qué hora salís?')).toBeTruthy()
  })

  // Behavior 2
  it('renders a SystemMessage for system-kind messages', () => {
    vi.mocked(useThreadPolling).mockReturnValue({ messages: [systemMessage], loading: false, error: null, refetch: vi.fn() })
    render(<ThreadView tripId={10} passengerUserId={2} />)
    expect(screen.getByText('Solicitud enviada')).toBeTruthy()
  })

  // Behavior 3
  it('renders a contact_warning system message with warning styles', () => {
    const warningMessage: Message = {
      id: 3,
      threadId: 99,
      kind: 'system',
      senderId: null,
      eventType: 'contact_warning',
      body: 'No compartas datos de contacto.',
      createdAt: '2026-06-01T10:02:00',
    }
    vi.mocked(useThreadPolling).mockReturnValue({ messages: [warningMessage], loading: false, error: null, refetch: vi.fn() })
    render(<ThreadView tripId={10} passengerUserId={2} />)
    const warning = screen.getByText('No compartas datos de contacto.')
    expect(warning).toBeTruthy()
    // Warning styling lives on the wrapping container (error-container background).
    const styled = warning.closest('div')
    expect(styled?.className).toContain('error')
  })

  // Behavior 4
  it('shows the closed notice and disables the composer when thread is closed', () => {
    vi.mocked(useThread).mockReturnValue({ thread: { ...baseThread, isClosed: true }, loading: false, error: null, refetch: vi.fn() })
    vi.mocked(useThreadPolling).mockReturnValue({ messages: [userMessage], loading: false, error: null, refetch: vi.fn() })
    render(<ThreadView tripId={10} passengerUserId={2} />)
    expect(
      screen.getByText('Este chat cerró. El viaje finalizó hace 24 horas.'),
    ).toBeTruthy()
    const composer = screen.getByLabelText('Mensaje') as HTMLTextAreaElement
    expect(composer.disabled).toBe(true)
  })
})
