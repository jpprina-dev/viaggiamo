'use client'

import { Footer } from '@/components/layout'
import {
  HeroSection,
  PopularTrips,
  BenefitsSection,
  CTASection,
  StatsSection,
  HowItWorksSection,
} from '@/features/home/components'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <HeroSection />
      <PopularTrips />
      <CTASection />
      <BenefitsSection />
      <StatsSection />
      <HowItWorksSection />
      <Footer />
    </div>
  )
}
