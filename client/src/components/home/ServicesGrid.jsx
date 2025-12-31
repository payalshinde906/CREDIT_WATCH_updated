import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

const services = [
  {
    title: 'Report Overdue Payer',
    desc: 'File overdue invoices with supporting docs and trigger formal follow-ups.',
    to: '/services/report-overdue',
    color: 'from-red-400 to-red-500',
  },
  {
    title: 'Credit Management',
    desc: 'Centralize payment reminders, validation workflows, and dispute tracking.',
    to: '/services/credit-management',
    color: 'from-blue-400 to-blue-500',
  },
  {
    title: 'Partners Credit Overdue Report',
    desc: 'Share structured overdue data with partner networks to reduce risk.',
    to: '/services/partners-report',
    color: 'from-emerald-400 to-emerald-500',
  },
  {
    title: 'Finalization Steps',
    desc: 'Lock the trade record with acknowledgment, settlement notes, and audit trails.',
    to: '/services/finalization',
    color: 'from-amber-400 to-amber-500',
  },
]

export default function ServicesGrid() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-heading font-bold mb-3">Services Overview</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Centralized credit intelligence workflows designed for GST-registered businesses.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {services.map((service, idx) => (
            <motion.div
              key={service.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
            >
              <Link to={service.to} className="block h-full group">
                <div className="card h-full">
                  <div className={`h-1.5 w-16 rounded-full bg-gradient-to-r ${service.color} mb-4 group-hover:w-20 transition-all`} />
                  <h3 className="text-xl font-heading font-semibold mb-2">{service.title}</h3>
                  <p className="text-gray-600 mb-4 text-sm">{service.desc}</p>
                  <span className="text-primary-700 font-semibold inline-flex items-center gap-1">
                    Learn more <span aria-hidden>→</span>
                  </span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
