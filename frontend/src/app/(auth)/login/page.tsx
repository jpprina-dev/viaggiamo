'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import toast from 'react-hot-toast'
import { GoogleOAuthProvider, CredentialResponse } from '@react-oauth/google'
import { login, loginWithGoogle } from '@/lib/auth'
import { useAuth } from '@/contexts/AuthContext'
import { AuthLayout, LoginForm, GoogleAuthButton } from '@/features/auth/components'
import { ROUTES } from '@/config/routes'
import type { LoginInput } from '@/types'

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''

function LoginFormWrapper() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, loading, refreshUser } = useAuth()
  
  // Get return URL from query params, default to profile
  const returnUrl = searchParams.get('returnUrl') || ROUTES.PROFILE

  // Redirect to profile if already authenticated
  useEffect(() => {
    if (!loading && user) {
      router.push(returnUrl)
    }
  }, [loading, user, router, returnUrl])

  const handleSubmit = async (data: LoginInput) => {
    setIsLoading(true)
    try {
      await login(data.email, data.password)
      await refreshUser()
      toast.success('¡Inicio de sesión exitoso!')
      router.push(returnUrl)
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
      router.push(returnUrl)
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

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-container border-r-transparent"></div>
          <p className="mt-4 text-on-surface-variant">Cargando...</p>
        </div>
      </div>
    )
  }

  return (
    <AuthLayout
      title="Iniciar Sesión"
      subtitle="¿No tienes cuenta?"
      subtitleLink={{
        text: '¿No tienes cuenta?',
        href: ROUTES.REGISTER,
        label: 'Regístrate aquí',
      }}
    >
      {/* Google Sign In */}
      <div className="mb-6">
        <GoogleAuthButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          text="Continuar con Google"
          disabled={isLoading}
        />
      </div>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-outline-variant"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-surface-container-lowest text-on-surface-variant">O continúa con email</span>
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
              className="h-4 w-4 text-primary accent-primary border-outline-variant rounded"
            />
            <label htmlFor="remember-me" className="ml-2 block text-on-surface text-sm">
              Recordarme
            </label>
          </div>
          <Link href={ROUTES.FORGOT_PASSWORD} className="font-semibold text-primary hover:text-primary/80 text-sm transition-colors">
            ¿Olvidaste tu contraseña?
          </Link>
        </div>

        <div className="text-center text-body-md text-on-surface-variant pt-4 border-t border-outline-variant/30">
          Al iniciar sesión, aceptas nuestros{' '}
          <Link href={ROUTES.TERMS} className="font-semibold text-primary hover:text-primary/80 transition-colors">
            Términos de Servicio
          </Link>{' '}
          y{' '}
          <Link href={ROUTES.PRIVACY} className="font-semibold text-primary hover:text-primary/80 transition-colors">
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
