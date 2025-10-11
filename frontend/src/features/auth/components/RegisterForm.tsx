'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff } from 'lucide-react'
import Link from 'next/link'
import { Input, Button } from '@/components/ui'
import type { RegisterInput } from '@/types'

const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  username: z.string().min(3, 'El nombre de usuario debe tener al menos 3 caracteres'),
  fullName: z.string().min(2, 'El nombre completo es requerido'),
  phone: z.string().optional(),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Las contraseñas no coinciden",
  path: ["confirmPassword"],
})

type RegisterFormData = z.infer<typeof registerSchema>

interface RegisterFormProps {
  onSubmit: (data: RegisterInput) => Promise<void>
  isLoading: boolean
}

export function RegisterForm({ onSubmit, isLoading }: RegisterFormProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const handleFormSubmit = async (data: RegisterFormData) => {
    await onSubmit({
      email: data.email,
      username: data.username,
      fullName: data.fullName,
      phone: data.phone,
      password: data.password,
    })
  }

  return (
    <form className="space-y-6" onSubmit={handleSubmit(handleFormSubmit)}>
      <Input
        label="Email"
        type="email"
        autoComplete="email"
        placeholder="tu@email.com"
        error={errors.email?.message}
        {...register('email')}
      />

      <Input
        label="Nombre de Usuario"
        type="text"
        autoComplete="username"
        placeholder="juan123"
        error={errors.username?.message}
        {...register('username')}
      />

      <Input
        label="Nombre Completo"
        type="text"
        autoComplete="name"
        placeholder="Juan Pérez"
        error={errors.fullName?.message}
        {...register('fullName')}
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
  )
}
