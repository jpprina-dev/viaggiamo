'use client'

import { Footer } from '@/components/layout'
import {
  HeroSection,
  PopularTrips,
  BenefitsSection,
  CTASection,
  // StatsSection, // TODO: feature to be included later
  HowItWorksSection,
} from '@/features/home/components'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-surface">
      {/* Dark hero with search */}
      <HeroSection />
      {/* Popular trips — surface-container-low */}
      <PopularTrips />
      {/* How it works — surface-container-low */}
      <HowItWorksSection />
      {/* Benefits — surface */}
      <BenefitsSection />
      {/* CTA — anchor-dark */}
      <CTASection />
      <Footer />
    </div>
  )
}
