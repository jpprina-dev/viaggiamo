/**
 * Constants for trip creation feature
 */

import React from 'react'
import { CigaretteOff, PawPrint, Baby } from 'lucide-react'
import type { TripPreference } from './types'

/**
 * Icon components for trip preferences
 * Can be customized with different sizes by passing className
 */
export const PREFERENCE_ICONS: Record<TripPreference, React.ReactNode> = {
  no_smoking: <CigaretteOff className="h-5 w-5" />,
  no_pets: <PawPrint className="h-5 w-5" />,
  no_children: <Baby className="h-5 w-5" />,
}

/**
 * Get preference icon with custom size
 * @param preference - The trip preference key
 * @param size - Icon size class (e.g., 'h-3 w-3', 'h-5 w-5')
 * @returns React node with the icon
 */
export function getPreferenceIcon(preference: TripPreference, size: string = 'h-5 w-5'): React.ReactNode {
  const iconMap: Record<TripPreference, React.ComponentType<{ className?: string }>> = {
    no_smoking: CigaretteOff,
    no_pets: PawPrint,
    no_children: Baby,
  }

  const IconComponent = iconMap[preference]
  return <IconComponent className={size} />
}
