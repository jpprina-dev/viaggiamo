'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { Input, Button } from '@/components/ui'
import type { RegisterInput } from '@/types'

const completeRegistrationSchema = z.object({
  username: z.string().min(3, 'El nombre de usuario debe tener al menos 3 caracteres'),
  name: z.string().min(2, 'El nombre es requerido'),
  last_name: z.string().min(2, 'El apellido es requerido'),
  phone: z.string().optional(),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Las contraseñas no coinciden",
  path: ["confirmPassword"],
})

type CompleteRegistrationFormData = z.infer<typeof completeRegistrationSchema>

interface CompleteRegistrationFormProps {
  email: string
  onSubmit: (data: RegisterInput) => Promise<void>
  onBack: () => void
  isLoading: boolean
}

export function CompleteRegistrationForm({
  email,
  onSubmit,
  onBack,
  isLoading
}: CompleteRegistrationFormProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CompleteRegistrationFormData>({
    resolver: zodResolver(completeRegistrationSchema),
  })

  const handleFormSubmit = async (data: CompleteRegistrationFormData) => {
    await onSubmit({
      email,
      username: data.username,
      name: data.name,
      last_name: data.last_name,
      phone: data.phone,
      password: data.password,
    })
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        type="button"
        onClick={onBack}
        className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Cambiar email</span>
      </button>

      {/* Email display (read-only) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-700">
          {email}
        </div>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
        <Input
          label="Nombre de Usuario"
          type="text"
          autoComplete="username"
          placeholder="juan123"
          error={errors.username?.message}
          {...register('username')}
        />

        <Input
          label="Nombre"
          type="text"
          autoComplete="given-name"
          placeholder="Juan"
          error={errors.name?.message}
          {...register('name')}
        />

        <Input
          label="Apellido"
          type="text"
          autoComplete="family-name"
          placeholder="Pérez"
          error={errors.last_name?.message}
          {...register('last_name')}
        />

        <Input
          label="Teléfono (opcional)"
          type="tel"
          autoComplete="tel"
          placeholder="+54 9 11 1234-5678"
          error={errors.phone?.message}
          {...register('phone')}
        />

        <Input
          label="Contraseña"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
          placeholder="••••••••"
          error={errors.password?.message}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="cursor-pointer"
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          }
          {...register('password')}
        />

        <Input
          label="Confirmar Contraseña"
          type={showConfirmPassword ? 'text' : 'password'}
          autoComplete="new-password"
          placeholder="••••••••"
          error={errors.confirmPassword?.message}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="cursor-pointer"
            >
              {showConfirmPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          }
          {...register('confirmPassword')}
        />

        <div className="flex items-center">
          <input
            id="terms"
            name="terms"
            type="checkbox"
            required
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label htmlFor="terms" className="ml-2 block text-sm text-gray-900">
            Acepto los{' '}
            <Link href="/terms" className="text-primary-600 hover:text-primary-500">
              términos y condiciones
            </Link>{' '}
            y la{' '}
            <Link href="/privacy" className="text-primary-600 hover:text-primary-500">
              política de privacidad
            </Link>
          </label>
        </div>

        <Button
          type="submit"
          fullWidth
          size="lg"
          isLoading={isLoading}
        >
          Crear Cuenta
        </Button>
      </form>
    </div>
  )
}
