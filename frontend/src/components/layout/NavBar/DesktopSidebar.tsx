'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { GradientIcon } from '@/components/GradientIcon'
import { SidebarItem } from './SidebarItem'
import { ProfilePopover } from './ProfilePopover'
import { LogoutConfirmModal } from './LogoutConfirmModal'
import { NAV_ITEMS } from './navItems'
import { ROUTES } from '@/config/routes'
import { cn } from '@/utils/cn'

export function DesktopSidebar() {
  const [expanded, setExpanded] = useState(false)
  const [popoverOpen, setPopoverOpen] = useState(false)
  const [logoutModalOpen, setLogoutModalOpen] = useState(false)
  const { logout } = useAuth()
  const pathname = usePathname()

  const isExpanded = expanded || popoverOpen
  const navItems = NAV_ITEMS.slice(1)

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 bottom-0 z-50 bg-[#21212b]/85 backdrop-blur-md flex-col hidden md:flex transition-all duration-300 ease-in-out',
        isExpanded ? 'w-[220px]' : 'w-16',
      )}
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
    >
      <Link
        href={ROUTES.HOME}
        className="flex items-center px-3 py-4 border-b border-white/10 flex-shrink-0 hover:bg-white/5 transition-colors"
      >
        <GradientIcon width={32} height={32} className="h-8 w-8 flex-shrink-0" />
        <span
          className={cn(
            'ml-3 text-lg font-bold text-primary-container whitespace-nowrap transition-all duration-300',
            isExpanded ? 'opacity-100 max-w-[140px]' : 'opacity-0 max-w-0 overflow-hidden',
          )}
        >
          Viajamos
        </span>
      </Link>

      <nav className="flex flex-col flex-1 p-2 space-y-1 mt-2">
        <ProfilePopover expanded={isExpanded} onOpenChange={setPopoverOpen} />

        {navItems.map(item => (
          <SidebarItem
            key={item.id}
            icon={item.icon}
            label={item.label}
            href={item.href}
            isActive={pathname === item.href}
            isDisabled={item.disabled}
            badge={item.badge}
            expanded={isExpanded}
          />
        ))}
      </nav>

      <div className="p-2 border-t border-white/10">
        <button
          onClick={() => setLogoutModalOpen(true)}
          aria-label="Cerrar Sesión"
          className="flex items-center w-full px-3 py-2 rounded-xl transition-colors text-error/70 hover:text-error hover:bg-error/10"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          <span
            className={cn(
              'ml-3 text-sm font-medium whitespace-nowrap transition-all duration-300',
              isExpanded ? 'opacity-100 max-w-[140px]' : 'opacity-0 max-w-0 overflow-hidden',
            )}
          >
            Cerrar Sesión
          </span>
        </button>
      </div>

      {logoutModalOpen && (
        <LogoutConfirmModal
          onConfirm={() => { setLogoutModalOpen(false); logout() }}
          onCancel={() => setLogoutModalOpen(false)}
        />
      )}
    </aside>
  )
}
