import Link from 'next/link'

interface NavLinkProps {
  href: string
  pathname: string
  children: React.ReactNode
}

export function NavLink({ href, pathname, children }: NavLinkProps) {
  const isActive = pathname === href

  return (
    <Link
      href={href}
      className={`font-medium transition-colors text-sm ${
        isActive
          ? 'text-primary-container font-semibold'
          : 'text-white/70 hover:text-primary-container'
      }`}
    >
      {children}
    </Link>
  )
}
