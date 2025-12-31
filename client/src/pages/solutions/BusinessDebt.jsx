import { motion } from 'framer-motion'

const points = [
  'Debt calendars with priority flags',
  'Negotiation playbooks and templates',
  'Settlement tracking and documentation',
  'Alerts for compliance and covenant dates',
]

export default function BusinessDebt() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Business Debt</h1>
          <p className="text-lg text-gray-600 mb-6">Manage liabilities with clarity and control.</p>
          <div className="card space-y-3">
            {points.map((p) => (
              <div key={p} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{p}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
