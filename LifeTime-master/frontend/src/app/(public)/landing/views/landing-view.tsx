import { LandingHeader } from '../components/landing-header'
import { LandingFooter } from '../components/landing-footer'
import { HeroSection } from '../sections/hero-section'
import { FeaturesSection } from '../sections/features-section'
import { HowItWorksSection } from '../sections/how-it-works-section'
import { PricingSection } from '../sections/pricing-section'
import { FaqSection } from '../sections/faq-section'

export function LandingView() {
  return (
    <>
      <LandingHeader />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <PricingSection />
        <FaqSection />
      </main>
      <LandingFooter />
    </>
  )
}
