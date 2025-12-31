import { motion } from 'framer-motion'

export default function CreditManagement() {
  const features = [
    'Smart reminder cadences with templates',
    'Dispute workspace with evidence vault',
    'Aging buckets and DSO visibility',
    'Role-based access for finance teams',
  ]

  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Credit Management</h1>
          <p className="text-lg text-gray-600 mb-6">Centralize follow-ups, disputes, and visibility across receivables.</p>
          <div className="card space-y-3">
            {features.map((feature) => (
              <div key={feature} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{feature}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
