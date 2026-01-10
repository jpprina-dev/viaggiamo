/**
 * CreateTripWizard - Multi-step form for creating a new trip
 */

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft, ArrowRight, Check } from 'lucide-react'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui'
import { StepIndicator } from './StepIndicator'
import { StepRoute } from './StepRoute'
import { StepDateTime } from './StepDateTime'
import { StepVehicle } from './StepVehicle'
import { StepPreferences } from './StepPreferences'
import { TripSummary } from './TripSummary'
import { useMyVehicles, useCreateTrip } from '../hooks'
import { 
  createTripFormSchema, 
  stepSchemas,
  type CreateTripFormData,
  type TripCreateInput 
} from '../types'
import { ROUTES } from '@/config/routes'

const STEPS = [
  { id: 1, title: 'Ruta' },
  { id: 2, title: 'Fecha' },
  { id: 3, title: 'Vehículo' },
  { id: 4, title: 'Preferencias' },
  { id: 5, title: 'Confirmar' },
]

export function CreateTripWizard() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const { vehicles, loading: vehiclesLoading } = useMyVehicles()
  const { createTrip, loading: isSubmitting } = useCreateTrip()

  const form = useForm<CreateTripFormData>({
    resolver: zodResolver(createTripFormSchema),
    defaultValues: {
      origin: '',
      destination: '',
      departureDate: '',
      departureTime: '',
      vehicleId: 0,
      totalSeats: 1,
      pricePerSeat: 0,
      tripPreferences: [],
      description: '',
      tripLegalComplianceAck: false,
    },
    mode: 'onChange',
  })

  const { register, handleSubmit, formState: { errors }, watch, setValue, trigger } = form

  const validateCurrentStep = async (): Promise<boolean> => {
    const stepIndex = currentStep - 1
    
    // For steps 1-4, validate the specific step fields
    if (stepIndex < stepSchemas.length) {
      const stepSchema = stepSchemas[stepIndex]
      const fieldsToValidate = Object.keys(stepSchema.shape) as (keyof CreateTripFormData)[]
      const isValid = await trigger(fieldsToValidate)
      return isValid
    }
    
    return true
  }

  const handleNext = async () => {
    const isValid = await validateCurrentStep()
    if (isValid && currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const onSubmit = async (data: CreateTripFormData) => {
    try {
      // Combine date and time into ISO datetime
      const departureDateTime = new Date(`${data.departureDate}T${data.departureTime}`)
      
      const tripInput: TripCreateInput = {
        origin: data.origin,
        destination: data.destination,
        departureTime: departureDateTime.toISOString(),
        vehicleId: data.vehicleId,
        totalSeats: data.totalSeats,
        pricePerSeat: data.pricePerSeat,
        description: data.description || undefined,
        tripPreferences: data.tripPreferences && data.tripPreferences.length > 0 
          ? { preferences: data.tripPreferences }
          : undefined,
        tripLegalComplianceAck: data.tripLegalComplianceAck,
      }

      const createdTrip = await createTrip(tripInput)
      
      toast.success('¡Viaje publicado exitosamente!')
      router.push(ROUTES.TRIP_DETAIL(createdTrip.id))
    } catch (error) {
      toast.error('Error al publicar el viaje. Por favor, intenta de nuevo.')
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <StepRoute register={register} errors={errors} />
      case 2:
        return <StepDateTime register={register} errors={errors} />
      case 3:
        return (
          <StepVehicle
            register={register}
            errors={errors}
            watch={watch}
            setValue={setValue}
            vehicles={vehicles}
            vehiclesLoading={vehiclesLoading}
          />
        )
      case 4:
        return (
          <StepPreferences
            register={register}
            errors={errors}
            watch={watch}
            setValue={setValue}
          />
        )
      case 5:
        return (
          <TripSummary
            register={register}
            errors={errors}
            watch={watch}
            vehicles={vehicles}
            isSubmitting={isSubmitting}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Step Indicator */}
      <StepIndicator steps={STEPS} currentStep={currentStep} />

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
          {renderStep()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Anterior
          </Button>

          {currentStep < STEPS.length ? (
            <Button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-2"
            >
              Siguiente
              <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 bg-gradient-to-r from-primary-600 to-emerald-600 hover:from-primary-700 hover:to-emerald-700"
            >
              {isSubmitting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent" />
                  Publicando...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4" />
                  Publicar viaje
                </>
              )}
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}

