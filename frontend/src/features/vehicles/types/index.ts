/**
 * Types for vehicles feature (CRUD)
 */

export interface Vehicle {
  id: number
  make: string
  model: string
  year: number
  color?: string
  licensePlate: string
  seats: number
  isActive: boolean
  vehicleLegalComplianceAck?: boolean
  createdAt: string
}

export interface VehicleCreateInput {
  make: string
  model: string
  year: number
  licensePlate: string
  seats: number
  color?: string
  isActive?: boolean
  vehicleLegalComplianceAck: boolean
}

export interface VehicleUpdateInput {
  make?: string
  model?: string
  year?: number
  licensePlate?: string
  seats?: number
  color?: string
  isActive?: boolean
  vehicleLegalComplianceAck?: boolean
}
