'use client'

import { useState } from 'react'
import Link from 'next/link'
import { X, LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { PROFILE_SUB_ITEMS } from './navItems'
import { LogoutConfirmModal } from './LogoutConfirmModal'

interface ProfileSheetProps {
  isOpen: boolean
  onClose: () => void
}

export function ProfileSheet({ isOpen, onClose }: ProfileSheetProps) {
  const { user, logout } = useAuth()
  const [logoutModalOpen, setLogoutModalOpen] = useState(false)

  if (!isOpen || !user) return null

  const fullName = `${user.name} ${user.last_name}`

  return (
    <>
      <div
        data-testid="profile-sheet-overlay"
        className="fixed inset-0 bg-black/60 z-50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div className="fixed bottom-0 left-0 right-0 bg-anchor-dark rounded-t-2xl z-50 overflow-y-auto max-h-[80vh]">
        <div className="flex justify-between items-center p-4 border-b border-white/10">
          <div>
            <p className="font-semibold text-white">{fullName}</p>
            <p className="text-sm text-white/60">{user.email}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Cerrar menú"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        <nav className="flex flex-col p-4 space-y-1">
          {PROFILE_SUB_ITEMS.map(item => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className="px-4 py-3 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              {item.label}
            </Link>
          ))}

          <div className="border-t border-white/10 mt-2 pt-2">
            <button
              onClick={() => setLogoutModalOpen(true)}
              className="w-full flex items-center space-x-2 px-4 py-3 text-error hover:bg-error/10 rounded-lg transition-colors text-left"
            >
              <LogOut className="h-5 w-5" />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </nav>
      </div>

      {logoutModalOpen && (
        <LogoutConfirmModal
          onConfirm={() => { setLogoutModalOpen(false); onClose(); logout() }}
          onCancel={() => setLogoutModalOpen(false)}
        />
      )}
    </>
  )
}
