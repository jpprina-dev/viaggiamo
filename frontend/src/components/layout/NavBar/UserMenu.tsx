'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { User as UserIcon, LogOut, Settings } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import type { User } from '@/types'

interface UserMenuProps {
  user: User
}

export function UserMenu({ user }: UserMenuProps) {
  const { logout } = useAuth()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const fullName = `${user.name} ${user.last_name}`

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center space-x-2 focus:outline-none"
      >
        {user.profile_picture ? (
          <img
            src={user.profile_picture}
            alt={fullName}
            className="w-10 h-10 rounded-full border-2 border-primary-500"
          />
        ) : (
          <div className="w-10 h-10 rounded-full bg-primary-100 border-2 border-primary-500 flex items-center justify-center">
            <span className="text-primary-700 font-bold text-lg">
              {user.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
        <span className="text-gray-700 font-medium">{fullName}</span>
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2">
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-medium text-gray-900">{fullName}</p>
            <p className="text-sm text-gray-500 truncate">{user.email}</p>
            {user.auth_provider && user.auth_provider !== 'local' && (
              <p className="text-xs text-primary-600 mt-1">
                Conectado con {user.auth_provider}
              </p>
            )}
          </div>

          <Link
            href="/dashboard"
            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            onClick={() => setShowDropdown(false)}
          >
            <UserIcon className="h-4 w-4" />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/profile"
            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            onClick={() => setShowDropdown(false)}
          >
            <UserIcon className="h-4 w-4" />
            <span>Mi Perfil</span>
          </Link>

          <Link
            href="/settings"
            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            onClick={() => setShowDropdown(false)}
          >
            <Settings className="h-4 w-4" />
            <span>Configuración</span>
          </Link>

          <div className="border-t border-gray-100 mt-2"></div>

          <button
            onClick={() => {
              setShowDropdown(false)
              logout()
            }}
            className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      )}
    </div>
  )
}
