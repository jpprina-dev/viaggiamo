import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ProfilePopover } from '../ProfilePopover'
import { ROUTES } from '@/config/routes'

const mockUser = {
  name: 'Juan',
  last_name: 'Pérez',
  email: 'juan@example.com',
  profile_picture: null,
}

vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({ user: mockUser, logout: vi.fn() }),
}))

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

describe('ProfilePopover', () => {
  it('renders the trigger button', () => {
    render(<ProfilePopover expanded={false} />)
    expect(screen.getByRole('button', { name: /mi perfil/i })).toBeInTheDocument()
  })

  it('sub-item links are not visible when closed', () => {
    render(<ProfilePopover expanded={false} />)
    expect(screen.queryByRole('link', { name: 'Configuración' })).toBeNull()
    expect(screen.queryByRole('link', { name: 'Acerca de' })).toBeNull()
    expect(screen.queryByRole('link', { name: 'Centro de Ayuda' })).toBeNull()
  })

  it('shows 4 sub-item links after clicking the trigger', () => {
    render(<ProfilePopover expanded={false} />)
    fireEvent.click(screen.getByRole('button', { name: /mi perfil/i }))
    expect(screen.getByRole('link', { name: 'Mi Perfil' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Configuración' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Acerca de' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Centro de Ayuda' })).toBeInTheDocument()
  })

  it('sub-items have correct hrefs', () => {
    render(<ProfilePopover expanded={false} />)
    fireEvent.click(screen.getByRole('button', { name: /mi perfil/i }))
    expect(screen.getByRole('link', { name: 'Mi Perfil' })).toHaveAttribute('href', ROUTES.PROFILE)
    expect(screen.getByRole('link', { name: 'Configuración' })).toHaveAttribute('href', ROUTES.SETTINGS)
    expect(screen.getByRole('link', { name: 'Acerca de' })).toHaveAttribute('href', ROUTES.ABOUT)
    expect(screen.getByRole('link', { name: 'Centro de Ayuda' })).toHaveAttribute('href', ROUTES.HELP)
  })

  it('shows user full name in popover header', () => {
    render(<ProfilePopover expanded={false} />)
    fireEvent.click(screen.getByRole('button', { name: /mi perfil/i }))
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument()
  })

  it('closes on mousedown outside the popover', () => {
    render(<ProfilePopover expanded={false} />)
    fireEvent.click(screen.getByRole('button', { name: /mi perfil/i }))
    expect(screen.getByRole('link', { name: 'Configuración' })).toBeInTheDocument()
    fireEvent.mouseDown(document.body)
    expect(screen.queryByRole('link', { name: 'Configuración' })).toBeNull()
  })
})
