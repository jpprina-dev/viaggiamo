/**
 * Constants for trip creation feature
 */

import { CigaretteOff, PawPrint, Baby } from 'lucide-react'
import type { TripPreference } from './types'
import React from 'react'

/**
 * Icon component types for trip preferences
 */
export const PREFERENCE_ICON_COMPONENTS: Record<TripPreference, React.ComponentType<{ className?: string }>> = {
  no_smoking: CigaretteOff,
  no_pets: PawPrint,
  no_children: Baby,
}

/**
 * Get preference icon with custom size
 * @param preference - The trip preference key
 * @param size - Icon size class (e.g., 'h-3 w-3', 'h-5 w-5')
 * @returns React node with the icon
 */
export function getPreferenceIcon(preference: TripPreference, size: string = 'h-5 w-5'): React.ReactNode {
  const IconComponent = PREFERENCE_ICON_COMPONENTS[preference]
  return React.createElement(IconComponent, { className: size })
}
