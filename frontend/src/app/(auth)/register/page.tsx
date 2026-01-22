'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { loginWithGoogle } from '@/lib/auth'
import { useAuth } from '@/contexts/AuthContext'
import {
  AuthLayout,
  EmailRegistrationForm,
  CompleteRegistrationForm
} from '@/features/auth/components'
import { ROUTES } from '@/config/routes'
import type { RegisterInput } from '@/types'

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''

function RegisterFormWrapper() {
  const [step, setStep] = useState<1 | 2>(1)
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { user, loading, refreshUser } = useAuth()

  // Redirect to profile if already authenticated
  useEffect(() => {
    if (!loading && user) {
      router.push(ROUTES.PROFILE)
    }
  }, [loading, user, router])

  const handleEmailSubmit = (submittedEmail: string) => {
    setEmail(submittedEmail)
    setStep(2)
  }

  const handleCompleteRegistration = async (data: RegisterInput) => {
    setIsLoading(true)
    try {
      const { register: registerUser } = await import('@/lib/auth')
      await registerUser(data)
      toast.success('¡Registro exitoso! Por favor inicia sesión.')
      router.push(ROUTES.LOGIN)
    } catch (error: any) {
      console.error('Register error:', error)
      const errorMessage = error.response?.errors?.[0]?.message || error.message || 'Error al registrarse'
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleBackToStep1 = () => {
    setStep(1)
    setEmail('')
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
      toast.success('¡Registro con Google exitoso!')
      router.push(ROUTES.PROFILE)
    } catch (error: any) {
      console.error('Google registration error:', error)
      toast.error(error.message || 'Error al registrarse con Google')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleError = () => {
    toast.error('Error al registrarse con Google')
  }

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  return (
    <AuthLayout
      title={step === 1 ? "Crear Cuenta" : "Completa tu Registro"}
      subtitle="¿Ya tienes cuenta?"
      subtitleLink={{
        text: '¿Ya tienes cuenta?',
        href: ROUTES.LOGIN,
        label: 'Inicia sesión aquí',
      }}
    >
      <div className="space-y-6">
        {step === 1 ? (
          <>
            {/* Google SSO */}
            <div className="mb-6">
              <div className="text-center mb-4">
                <span className="text-sm text-gray-500">Regístrate con Google</span>
              </div>
              <div className="flex justify-center">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  theme="outline"
                  size="large"
                  text="signup_with"
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

            {/* Email Registration Form */}
            <EmailRegistrationForm onSubmit={handleEmailSubmit} isLoading={isLoading} />
          </>
        ) : (
          <CompleteRegistrationForm
            email={email}
            onSubmit={handleCompleteRegistration}
            onBack={handleBackToStep1}
            isLoading={isLoading}
          />
        )}
      </div>
    </AuthLayout>
  )
}

export default function RegisterPage() {
  const clientId = GOOGLE_CLIENT_ID || '59753773929-6g41npfin0ef0hcte6jhssejsd7oqdnv.apps.googleusercontent.com'

  if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Configuración Requerida</h2>
          <p className="text-gray-600">
            Por favor configura NEXT_PUBLIC_GOOGLE_CLIENT_ID en las variables de entorno
          </p>
        </div>
      </div>
    )
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <RegisterFormWrapper />
    </GoogleOAuthProvider>
  )
}
