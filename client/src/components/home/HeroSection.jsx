import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

const tiles = [
  { title: 'Partners Credit Overdue Report', to: '/services/partners-report' },
  { title: 'Payment Follow-ups', to: '/services/credit-management' },
  { title: 'Report Overdue Payer', to: '/services/report-overdue' },
  { title: 'Finalization', to: '/services/finalization' },
  { title: 'Legal Service', to: '/offerings' },
]

export default function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 text-white section-padding relative overflow-hidden">
      <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top,_#60a5fa,_transparent_45%)]" aria-hidden />
      <div className="container-custom grid gap-12 lg:grid-cols-[1.1fr_1fr] items-center">
        <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}>
          <p className="inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-sm font-semibold text-primary-100 mb-4">
            GST-Registered Businesses Only
          </p>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold leading-tight mb-6">
            India’s Credit Intelligence Hub – Streamline Your Business Credit Transactions
          </h1>
          <p className="text-lg md:text-xl text-primary-100 mb-8 max-w-2xl">
            Mutual transaction acknowledgment and formal validation between buyers and suppliers. Report overdue payers, manage collections, and protect your trade lines.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/services/report-overdue" className="btn-accent shadow-xl">
              Report Overdue Payer
            </Link>
            <Link to="/appointment" className="btn-secondary bg-white/10 border-white text-white hover:bg-white/20">
              Book Appointment
            </Link>
          </div>
          <div className="mt-8 flex flex-wrap gap-4 text-sm text-primary-100">
            <span className="inline-flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-accent-300" /> Formal trade validation
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-accent-300" /> Collections-ready workflows
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-accent-300" /> Secure GST-first access
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="grid grid-cols-2 md:grid-cols-3 gap-4"
        >
          {tiles.map((tile, idx) => (
            <Link key={tile.title} to={tile.to} className="group">
              <div className="card h-full bg-white/10 border border-white/10 text-white backdrop-blur-md">
                <div className="flex items-start justify-between">
                  <p className="font-semibold leading-snug">{tile.title}</p>
                  <motion.span
                    whileHover={{ rotate: 10 }}
                    className="text-xs text-primary-100"
                  >
                    →
                  </motion.span>
                </div>
                <div className="mt-3 h-1 w-12 rounded-full bg-accent-400 group-hover:w-16 transition-all" />
              </div>
            </Link>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
