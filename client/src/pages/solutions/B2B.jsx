import { motion } from 'framer-motion'

const features = [
  'Multi-entity access controls and approvals',
  'Portfolio analytics with risk scoring',
  'ERP-friendly data exports and API roadmap',
  'Bulk overdue filing with templated uploads',
]

export default function B2B() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">B2B Solutions</h1>
          <p className="text-lg text-gray-600 mb-6">Enterprise-grade controls for complex buyer-supplier networks.</p>
          <div className="card space-y-3">
            {features.map((f) => (
              <div key={f} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{f}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
