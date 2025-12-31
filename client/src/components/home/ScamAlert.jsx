import { motion } from 'framer-motion'

export default function ScamAlert() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-gradient-to-r from-red-50 to-amber-50 border-l-4 border-red-500 py-6"
    >
      <div className="container-custom flex gap-4">
        <div className="mt-1">
          <svg className="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-heading font-bold text-red-900 mb-1">Fraud Alert</h3>
          <p className="text-red-800 text-sm md:text-base">
            Formalize every trade acknowledgment inside CreditDataWatch. Avoid payment scams, informal IOUs, and non-GST transactions. Only GST-validated entities gain access.
          </p>
          <ul className="mt-2 text-sm text-red-800 space-y-1">
            <li>• Never pay upfront for collections promises.</li>
            <li>• Validate GSTIN before sharing invoices or POs.</li>
            <li>• Report overdue payers immediately to protect your credit reputation.</li>
          </ul>
        </div>
      </div>
    </motion.section>
  )
}
