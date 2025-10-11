'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input, Button } from '@/components/ui'

const emailSchema = z.object({
  email: z.string().email('Email inválido'),
})

type EmailFormData = z.infer<typeof emailSchema>

interface EmailRegistrationFormProps {
  onSubmit: (email: string) => void
  isLoading?: boolean
}

export function EmailRegistrationForm({ onSubmit, isLoading = false }: EmailRegistrationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema),
  })

  const handleFormSubmit = (data: EmailFormData) => {
    onSubmit(data.email)
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

      <Button
        type="submit"
        fullWidth
        size="lg"
        isLoading={isLoading}
      >
        Continuar con Email
      </Button>
    </form>
  )
}
