import { motion } from 'framer-motion'

export default function About() {
  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">About CreditDataWatch</h1>
          <p className="text-lg text-gray-600 mb-6">
            CreditDataWatch is India’s GST-first credit intelligence hub helping enterprises and MSMEs formalize trade acknowledgments, report overdue payers, and manage collections with confidence.
          </p>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="card">
              <h3 className="text-xl font-heading font-semibold mb-2">Why we exist</h3>
              <p className="text-gray-700 text-sm">
                Cash-flow disruption from delayed payments hurts growth. We bring structure, transparency, and accountability to B2B transactions so businesses stay liquid and creditworthy.
              </p>
            </div>
            <div className="card">
              <h3 className="text-xl font-heading font-semibold mb-2">What we value</h3>
              <p className="text-gray-700 text-sm">
                Compliance, trust, and speed. Every workflow is built to be GST-compliant, auditable, and fast to execute with minimal manual effort.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
