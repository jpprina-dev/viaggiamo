import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProfileSheet } from '../ProfileSheet'
import { ROUTES } from '@/config/routes'

const mockLogout = vi.fn()
const mockUser = {
  id: 1,
  name: 'Ana',
  last_name: 'García',
  email: 'ana@example.com',
  username: 'ana_garcia',
  status: 'active',
  email_verified: true,
  phone: '+34123456789',
  phone_verified: true,
  profile_picture: null,
  profile_short_bio: 'Test bio',
  auth_provider: 'local',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: mockUser, logout: mockLogout }),
}))

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

describe('ProfileSheet', () => {
  it('renders nothing when isOpen is false', () => {
    const { container } = render(<ProfileSheet isOpen={false} onClose={vi.fn()} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders 4 sub-item links when open', () => {
    render(<ProfileSheet isOpen={true} onClose={vi.fn()} />)
    expect(screen.getByRole('link', { name: 'Mi Perfil' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Configuración' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Acerca de' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Centro de Ayuda' })).toBeInTheDocument()
  })

  it('sub-items have correct hrefs', () => {
    render(<ProfileSheet isOpen={true} onClose={vi.fn()} />)
    expect(screen.getByRole('link', { name: 'Mi Perfil' })).toHaveAttribute('href', ROUTES.PROFILE)
    expect(screen.getByRole('link', { name: 'Configuración' })).toHaveAttribute('href', ROUTES.SETTINGS)
    expect(screen.getByRole('link', { name: 'Acerca de' })).toHaveAttribute('href', ROUTES.ABOUT)
    expect(screen.getByRole('link', { name: 'Centro de Ayuda' })).toHaveAttribute('href', ROUTES.HELP)
  })

  it('renders Cerrar Sesión button when open', () => {
    render(<ProfileSheet isOpen={true} onClose={vi.fn()} />)
    expect(screen.getByRole('button', { name: /cerrar sesión/i })).toBeInTheDocument()
  })

  it('calls onClose when overlay is clicked', () => {
    const onClose = vi.fn()
    render(<ProfileSheet isOpen={true} onClose={onClose} />)
    fireEvent.click(screen.getByTestId('profile-sheet-overlay'))
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('calls logout and onClose when Cerrar Sesión is clicked', () => {
    const onClose = vi.fn()
    mockLogout.mockClear()
    render(<ProfileSheet isOpen={true} onClose={onClose} />)
    fireEvent.click(screen.getByRole('button', { name: /cerrar sesión/i }))
    expect(mockLogout).toHaveBeenCalledOnce()
    expect(onClose).toHaveBeenCalledOnce()
  })
})
