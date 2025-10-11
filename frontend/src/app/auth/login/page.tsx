'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { login, loginWithGoogle } from '@/lib/auth'
import { useAuth } from '@/contexts/AuthContext'
import { AuthLayout, LoginForm } from '@/features/auth/components'
import type { LoginInput } from '@/types'

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''

function LoginFormWrapper() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { refreshUser } = useAuth()

  const handleSubmit = async (data: LoginInput) => {
    setIsLoading(true)
    try {
      await login(data.email, data.password)
      await refreshUser()
      toast.success('¡Inicio de sesión exitoso!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('Login error:', error)
      toast.error(error.message || 'Error al iniciar sesión')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      toast.error('Error al obtener credenciales de Google')
      return
    }

    setIsLoading(true)
    try {
      await loginWithGoogle(credentialResponse.credential)
      await refreshUser()
      toast.success('¡Inicio de sesión con Google exitoso!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('Google login error:', error)
      toast.error(error.message || 'Error al iniciar sesión con Google')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleError = () => {
    toast.error('Error al iniciar sesión con Google')
  }

  return (
    <AuthLayout
      title="Iniciar Sesión"
      subtitle="¿No tienes cuenta?"
      subtitleLink={{
        text: '¿No tienes cuenta?',
        href: '/auth/register',
        label: 'Regístrate aquí',
      }}
    >
      {/* Google Sign In */}
      <div className="mb-6">
        <div className="text-center mb-4">
          <span className="text-sm text-gray-500">Inicia sesión con Google</span>
        </div>
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            theme="outline"
            size="large"
            text="signin_with"
            width="100%"
          />
        </div>
      </div>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">O continúa con email</span>
        </div>
      </div>

      {/* Email/Password Form */}
      <LoginForm onSubmit={handleSubmit} isLoading={isLoading} />

      {/* Additional Options */}
      <div className="mt-4 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="remember-me" className="ml-2 block text-gray-900">
              Recordarme
            </label>
          </div>
          <Link href="/auth/forgot-password" className="font-medium text-primary-600 hover:text-primary-500">
            ¿Olvidaste tu contraseña?
          </Link>
        </div>

        <div className="text-center text-sm text-gray-600 pt-4 border-t border-gray-200">
          Al iniciar sesión, aceptas nuestros{' '}
          <Link href="/terms" className="text-primary-600 hover:text-primary-500">
            Términos de Servicio
          </Link>{' '}
          y{' '}
          <Link href="/privacy" className="text-primary-600 hover:text-primary-500">
            Política de Privacidad
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}

export default function LoginPage() {
  const clientId = GOOGLE_CLIENT_ID || '59753773929-6g41npfin0ef0hcte6jhssejsd7oqdnv.apps.googleusercontent.com'

  if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Configuración Requerida</h2>
          <p className="text-gray-600">
            Por favor configura NEXT_PUBLIC_GOOGLE_CLIENT_ID en las variables de entorno
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Valor actual: {GOOGLE_CLIENT_ID || 'undefined'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <LoginFormWrapper />
    </GoogleOAuthProvider>
  )
}
