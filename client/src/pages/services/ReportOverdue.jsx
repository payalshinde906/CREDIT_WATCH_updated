import { motion } from 'framer-motion'

export default function ReportOverdue() {
  const steps = [
    'Upload invoice, PO, and delivery proofs',
    'Validate counterparty GSTIN',
    'Send structured reminder and acknowledgement requests',
    'Escalate to partner network and legal options if unpaid',
  ]

  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Report Overdue Payer</h1>
          <p className="text-lg text-gray-600 mb-6">
            File overdue invoices, capture acknowledgments, and trigger compliant reminders.
          </p>
          <div className="card space-y-3">
            {steps.map((step) => (
              <div key={step} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
                <p className="text-gray-700">{step}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
