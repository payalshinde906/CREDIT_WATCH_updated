import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const services = [
  { title: 'Report Overdue Payer', to: '/services/report-overdue', summary: 'File overdue invoices with documents and acknowledgments.' },
  { title: 'Credit Management', to: '/services/credit-management', summary: 'Centralize reminders, disputes, and payment plans.' },
  { title: 'Partners Credit Overdue Report', to: '/services/partners-report', summary: 'Share structured overdue data with partner networks.' },
  { title: 'Finalization Steps', to: '/services/finalization', summary: 'Close the loop with settlement notes and audit trails.' },
]

export default function Services() {
  return (
    <section className="section-padding">
      <div className="container-custom">
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-heading font-bold mb-3">Services</h1>
          <p className="text-lg text-gray-600">Purpose-built workflows to keep business credit healthy.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {services.map((service, idx) => (
            <motion.div
              key={service.title}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              className="card flex flex-col gap-3"
            >
              <h3 className="text-2xl font-heading font-semibold">{service.title}</h3>
              <p className="text-gray-700 text-sm">{service.summary}</p>
              <div className="flex gap-3">
                <Link to={service.to} className="btn-primary">Open</Link>
                <Link to="/appointment" className="btn-secondary">Talk to us</Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
