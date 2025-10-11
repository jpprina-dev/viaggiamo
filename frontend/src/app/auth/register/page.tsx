'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { AuthLayout, RegisterForm } from '@/features/auth/components'
import type { RegisterInput } from '@/types'

export default function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (data: RegisterInput) => {
    setIsLoading(true)
    try {
      const { register: registerUser } = await import('@/lib/auth')
      await registerUser(data)
      toast.success('¡Registro exitoso! Por favor inicia sesión.')
      router.push('/auth/login')
    } catch (error: any) {
      console.error('Register error:', error)
      const errorMessage = error.response?.errors?.[0]?.message || error.message || 'Error al registrarse'
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Crear Cuenta"
      subtitle="¿Ya tienes cuenta?"
      subtitleLink={{
        text: '¿Ya tienes cuenta?',
        href: '/auth/login',
        label: 'Inicia sesión aquí',
      }}
    >
      <div>
        <RegisterForm onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </AuthLayout>
  )
}
