import HeroSection from '../components/home/HeroSection'
import ScamAlert from '../components/home/ScamAlert'
import ServicesGrid from '../components/home/ServicesGrid'
import SolutionsSection from '../components/home/SolutionsSection'
import StatsSection from '../components/home/StatsSection'
import Testimonial from '../components/home/Testimonial'
import FAQSection from '../components/home/FAQSection'
import CTASection from '../components/home/CTASection'

export default function Home() {
  return (
    <>
      <HeroSection />
      <ScamAlert />
      <ServicesGrid />
      <SolutionsSection />
      <StatsSection />
      <Testimonial />
      <FAQSection />
      <CTASection />
    </>
  )
}
