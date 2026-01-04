import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function PartnersReport() {
  const features = [
    'Access verified defaulter reports from our partner network',
    'Cross-reference credit histories across industries',
    'Early warning system for potential defaults',
    'Comprehensive credit risk assessment',
    'Industry-specific defaulter trends and patterns',
  ]

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
          
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">Partners Credit Overdue Report</h1>
            <p className="text-xl text-gray-600">Leverage collective intelligence from our partner network</p>
          </div>

          {/* Main Description */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Access Network-Wide Credit Intelligence</h2>
            <p className="text-gray-700 leading-relaxed">
              Partners Credit Overdue Report provides you access to a comprehensive database of defaulter information collected from our entire network of registered businesses. This collaborative approach helps businesses make informed decisions before extending credit.
            </p>
            <p className="text-gray-700 leading-relaxed">
              All reports are verified by CreditDataWatch specialists to ensure accuracy and reliability. Get insights into payment behaviors, dispute histories, and settlement patterns across India.
            </p>
          </div>

          {/* Features */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">What You Get</h2>
            <div className="space-y-3">
              {features.map((feature) => (
                <div key={feature} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-primary-600 flex-shrink-0" />
                  <p className="text-gray-700">{feature}</p>
                </div>
              ))}
            </div>
          </div>

          {/* How It Works */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">How It Works</h2>
            <div className="space-y-3">
              <p className="text-gray-700 leading-relaxed">
                <strong>1. Search by GSTIN or PAN:</strong> Enter the business identifier of the party you want to check.
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>2. View Verified Reports:</strong> Access all verified defaulter cases reported by our partner network.
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>3. Analyze Risk:</strong> Review payment history, outstanding amounts, and settlement status.
              </p>
              <p className="text-gray-700 leading-relaxed">
                <strong>4. Make Informed Decisions:</strong> Use this intelligence to decide credit terms and limits.
              </p>
            </div>
          </div>

          {/* Membership Note */}
          <div className="card bg-amber-50 border-amber-200">
            <h3 className="text-lg font-heading font-bold text-amber-900 mb-2">Subscription Required</h3>
            <p className="text-gray-700 mb-3">
              Access to Partners Credit Overdue Reports requires an active subscription plan. Different plans offer varying levels of access to report history and analytics.
            </p>
            <Link to="/membership" className="btn-primary inline-block">
              View Subscription Plans
            </Link>
          </div>

          {/* CTA Section */}
          <div className="card bg-primary-50 border-primary-200 text-center space-y-4">
            <h3 className="text-2xl font-heading font-bold text-primary-900">Ready to Access Partner Reports?</h3>
            <p className="text-gray-700">Schedule a consultation to learn more about our partner network</p>
            <Link to="/appointment" className="btn-primary inline-block">
              Book Appointment
            </Link>
          </div>

        </motion.div>
      </div>
    </section>
  )
}
