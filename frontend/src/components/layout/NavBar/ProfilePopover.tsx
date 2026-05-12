'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { PROFILE_SUB_ITEMS } from './navItems'
import { cn } from '@/utils/cn'

interface ProfilePopoverProps {
  expanded: boolean
  onOpenChange?: (open: boolean) => void
}

export function ProfilePopover({ expanded, onOpenChange }: ProfilePopoverProps) {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const updateOpen = useCallback((next: boolean) => {
    setOpen(next)
    onOpenChange?.(next)
  }, [onOpenChange])

  useEffect(() => {
    function onOutsideClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) updateOpen(false)
    }
    document.addEventListener('mousedown', onOutsideClick)
    return () => document.removeEventListener('mousedown', onOutsideClick)
  }, [updateOpen])

  if (!user) return null

  const fullName = `${user.name} ${user.last_name}`

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => updateOpen(!open)}
        aria-label="Mi Perfil"
        aria-expanded={open}
        className={cn(
          'flex items-center w-full px-3 py-2 rounded-xl transition-colors hover:bg-white/10',
          open && 'bg-white/10',
        )}
      >
        <div className="w-8 h-8 rounded-full bg-secondary-container border-2 border-primary-container flex items-center justify-center flex-shrink-0">
          <span className="text-secondary font-bold text-sm">
            {user.name.charAt(0).toUpperCase()}
          </span>
        </div>
        {expanded && (
          <span className="ml-3 text-sm font-medium text-white/80 whitespace-nowrap transition-all duration-300 opacity-100 max-w-[140px]">
            {fullName}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute left-full top-0 ml-2 w-56 bg-anchor-dark border border-white/10 rounded-xl shadow-ambient-lg py-2 z-[60]">
          <div className="px-4 py-3 border-b border-white/10 mb-1">
            <p className="font-semibold text-white text-sm">{fullName}</p>
            <p className="text-xs text-white/60 truncate">{user.email}</p>
          </div>
          {PROFILE_SUB_ITEMS.map(item => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => updateOpen(false)}
              className="block px-4 py-2 text-sm text-white/80 hover:text-white hover:bg-white/10 transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
