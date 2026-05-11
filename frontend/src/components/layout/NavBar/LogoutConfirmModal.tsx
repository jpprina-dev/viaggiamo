'use client'

import { createPortal } from 'react-dom'
import { LogOut } from 'lucide-react'
import { Button } from '@/components/ui'

interface LogoutConfirmModalProps {
  onConfirm: () => void
  onCancel: () => void
}

export function LogoutConfirmModal({ onConfirm, onCancel }: LogoutConfirmModalProps) {
  return createPortal(
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onCancel}
        aria-hidden="true"
      />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-xl bg-white p-6 shadow-xl transition-all border border-gray-200">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
            <LogOut className="h-6 w-6 text-red-600" />
          </div>
          <div className="mt-4 text-center">
            <h3 className="text-lg font-semibold text-gray-900">
              ¿Cerrar sesión?
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Vas a salir de tu cuenta.<br />Podés volver a iniciar sesión cuando quieras.
            </p>
          </div>
          <div className="mt-6 flex gap-3">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={onCancel}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="danger"
              className="flex-1"
              onClick={onConfirm}
            >
              Cerrar Sesión
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}
