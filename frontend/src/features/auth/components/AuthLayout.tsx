import Link from 'next/link'
import { GradientIcon } from '@/components/GradientIcon'

interface AuthLayoutProps {
  title: string
  subtitle?: string
  subtitleLink?: {
    text: string
    href: string
    label: string
  }
  children: React.ReactNode
}

export function AuthLayout({ title, subtitle, subtitleLink, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen relative flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Background: Argentine landscape feel with anchor-dark gradient */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(135deg, #21212b 0%, #1a2a1e 50%, #21212b 100%)',
        }}
      />
      {/* Pin watermark texture */}
      <div className="absolute inset-0 bg-pin-watermark opacity-60" />
      {/* Soft teal accent glow */}
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 60% 50% at 30% 60%, rgba(150,243,233,0.07) 0%, transparent 70%)',
        }}
      />

      {/* Glass card */}
      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2 mb-8">
          <GradientIcon width={36} height={36} />
          <span className="text-2xl font-bold text-primary-container">Viajamos</span>
        </Link>

        {/* Card */}
        <div className="glass rounded-2xl p-8 shadow-ambient-lg">
          {/* Title */}
          <div className="mb-6">
            <h1 className="text-headline-sm text-on-surface font-bold">{title}</h1>
            {subtitle && subtitleLink && (
              <p className="mt-1.5 text-body-md text-on-surface-variant">
                {subtitleLink.text}{' '}
                <Link
                  href={subtitleLink.href}
                  className="font-semibold text-primary hover:text-primary/80 transition-colors"
                >
                  {subtitleLink.label}
                </Link>
              </p>
            )}
          </div>

          {children}
        </div>
      </div>
    </div>
  )
}
