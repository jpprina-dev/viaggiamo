'use client'

import { useAuth } from '@/contexts/AuthContext'
import { NavBar, Footer } from '@/components/layout'
import {
  HeroSection,
  PopularTrips,
  BenefitsSection,
  CTASection,
  StatsSection,
  HowItWorksSection,
} from '@/features/home/components'

export default function HomePage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-white">
      <NavBar />
      <HeroSection user={user} />
      <PopularTrips />
      <CTASection />
      <BenefitsSection />
      <StatsSection />
      <HowItWorksSection />
      <Footer />
    </div>
  )
}
