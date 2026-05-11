'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { ProfileSheet } from './ProfileSheet'
import { NAV_ITEMS, PROFILE_SUB_ITEMS } from './navItems'
import { cn } from '@/utils/cn'

const PROFILE_ACTIVE_PATHS = PROFILE_SUB_ITEMS.map(item => item.href)

export function MobileBottomNav() {
  const { user } = useAuth()
  const pathname = usePathname()
  const [sheetOpen, setSheetOpen] = useState(false)

  if (!user) return null

  const otherItems = NAV_ITEMS.slice(1)
  const isProfileActive = PROFILE_ACTIVE_PATHS.some(p => pathname.startsWith(p))

  return (
    <>
      <nav className="fixed bottom-0 left-0 right-0 h-20 bg-anchor-dark border-t border-white/10 flex items-center justify-around px-2 z-50 md:hidden">
        <button
          onClick={() => setSheetOpen(true)}
          aria-label="Mi Perfil"
          className={cn(
            'flex flex-col items-center justify-center gap-1 w-14 h-16 rounded-xl transition-colors',
            isProfileActive
              ? 'bg-primary-container text-[#00210b]'
              : 'text-white/70 hover:text-white hover:bg-white/10',
          )}
        >
          <User className="w-5 h-5" />
          <span className="text-[10px] font-medium leading-none">Perfil</span>
        </button>

        {otherItems.map(item => {
          const Icon = item.icon
          const isActive = pathname === item.href

          if (item.disabled) {
            return (
              <div
                key={item.id}
                className="relative flex flex-col items-center justify-center gap-1 w-14 h-16 rounded-xl text-white/30 cursor-not-allowed"
                aria-label={item.label}
                aria-disabled="true"
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-medium leading-none">{item.shortLabel}</span>
                {item.badge && (
                  <span className="absolute -top-0.5 -right-0.5 text-[8px] bg-white/10 text-white/50 px-1 rounded-full leading-4">
                    {item.badge}
                  </span>
                )}
              </div>
            )
          }

          return (
            <Link
              key={item.id}
              href={item.href}
              aria-label={item.label}
              className={cn(
                'flex flex-col items-center justify-center gap-1 w-14 h-16 rounded-xl transition-colors',
                isActive
                  ? 'bg-primary-container text-[#00210b]'
                  : 'text-white/70 hover:text-white hover:bg-white/10',
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium leading-none">{item.shortLabel}</span>
            </Link>
          )
        })}
      </nav>

      <ProfileSheet isOpen={sheetOpen} onClose={() => setSheetOpen(false)} />
    </>
  )
}
