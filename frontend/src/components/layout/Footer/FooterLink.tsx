import Link from 'next/link'

interface FooterLinkProps {
  href: string
  children: React.ReactNode
}

export function FooterLink({ href, children }: FooterLinkProps) {
  return (
    <li>
      <Link href={href} className="text-white/40 hover:text-secondary-container transition-colors">
        {children}
      </Link>
    </li>
  )
}
