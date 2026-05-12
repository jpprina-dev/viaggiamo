import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { GuestHeader } from '../GuestHeader'

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

vi.mock('@/components/GradientIcon', () => ({
  GradientIcon: () => <svg data-testid="gradient-icon" />,
}))

describe('GuestHeader', () => {
  it('renders the logo linking to /', () => {
    render(<GuestHeader />)
    const logoLink = screen.getByRole('link', { name: /viajamos/i })
    expect(logoLink).toHaveAttribute('href', '/')
  })

  it('renders Iniciar Sesión linking to /login', () => {
    render(<GuestHeader />)
    const loginLink = screen.getByRole('link', { name: /iniciar sesión/i })
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('renders Crear Cuenta linking to /register', () => {
    render(<GuestHeader />)
    const registerLink = screen.getByRole('link', { name: /crear cuenta/i })
    expect(registerLink).toHaveAttribute('href', '/register')
  })

  it('does not render section navigation links', () => {
    render(<GuestHeader />)
    expect(screen.queryByRole('link', { name: /buscar/i })).toBeNull()
    expect(screen.queryByRole('link', { name: /mis viajes/i })).toBeNull()
    expect(screen.queryByRole('link', { name: /publicar/i })).toBeNull()
    expect(screen.queryByRole('link', { name: /mi perfil/i })).toBeNull()
  })

  it('renders exactly 3 links total (logo, login, register)', () => {
    render(<GuestHeader />)
    expect(screen.getAllByRole('link')).toHaveLength(3)
  })
})
