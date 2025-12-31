import { motion } from 'framer-motion'

export default function PartnersReport() {
  const bullets = [
    'Share overdue intelligence with vetted partners',
    'Standardized report formats for faster decisions',
    'Privacy-safe sharing with consent trails',
    'API-ready payloads for partner platforms (roadmap)',
  ]

  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Partners Credit Overdue Report</h1>
          <p className="text-lg text-gray-600 mb-6">
            Collaborate with credit networks by sharing structured overdue data responsibly.
          </p>
          <div className="card space-y-3">
            {bullets.map((item) => (
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
