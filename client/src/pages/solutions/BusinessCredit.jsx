import { motion } from 'framer-motion'

const bullets = [
  'Submit positive trade lines to improve credit posture',
  'Track bureau-like indicators and score movements',
  'Identity verification and compliance checks',
  'Action cards to maintain healthy credit utilization',
]

export default function BusinessCredit() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Business Credit</h1>
          <p className="text-lg text-gray-600 mb-6">Build and protect your business credit with verified data.</p>
          <div className="card space-y-3">
            {bullets.map((b) => (
              <div key={b} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{b}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
