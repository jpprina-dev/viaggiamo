'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'

/**
 * Component that scrolls to top on route change
 * This ensures users always start at the top of the page when navigating
 */
export function ScrollToTop() {
  const pathname = usePathname()

  useEffect(() => {
    // Scroll to top when pathname changes
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'instant', // Use 'instant' for immediate scroll, 'smooth' for animated
    })
  }, [pathname])

  return null
}
