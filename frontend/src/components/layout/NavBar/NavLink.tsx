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
      className={`font-medium transition-colors ${
        isActive
          ? 'text-primary-600 font-semibold'
          : 'text-gray-600 hover:text-primary-600'
      }`}
    >
      {children}
    </Link>
  )
}
