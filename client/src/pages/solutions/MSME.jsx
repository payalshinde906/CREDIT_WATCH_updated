import { motion } from 'framer-motion'

const items = [
  'Guided overdue filing in under 5 minutes',
  'Automated reminders with ready templates',
  'Simple dashboards for founders and accountants',
  'Access to partner overdue intelligence',
]

export default function MSME() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">MSME Solutions</h1>
          <p className="text-lg text-gray-600 mb-6">Streamlined credit workflows tailored for lean teams.</p>
          <div className="card space-y-3">
            {items.map((item) => (
              <div key={item} className="flex items-start gap-3">
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
