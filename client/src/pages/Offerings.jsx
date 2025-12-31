import { motion } from 'framer-motion'

const offerings = [
  'Formal trade validation workflows',
  'Portfolio-level credit dashboards',
  'Automated payment reminders and nudges',
  'Structured dispute resolution',
  'Audit-ready finalization steps',
  'API hooks for ERP/Accounting tools (coming soon)',
]

export default function Offerings() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Offerings</h1>
          <p className="text-lg text-gray-600 mb-6">
            Everything you need to monitor, validate, and protect B2B credit across your buyer-supplier network.
          </p>
          <div className="space-y-3">
            {offerings.map((item) => (
              <div key={item} className="card flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
