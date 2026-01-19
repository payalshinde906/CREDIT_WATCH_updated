import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function CTASection() {
  return (
    <section className="section-padding bg-gradient-to-r from-primary-700 via-primary-600 to-primary-700 text-white">
      <div className="container-custom text-center max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="text-3xl md:text-4xl font-heading font-bold mb-4">Ready to begin?</h2>
          <p className="text-primary-100 text-lg mb-6">
            Formalize your trade acknowledgments, reduce risk, and accelerate collections.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/appointment" className="btn-accent bg-white text-primary-700 hover:bg-gray-100">
              Book Appointment
            </Link>
            <Link to="/auth" className="btn-accent bg-white text-primary-700 hover:bg-gray-100">
              Login / Register
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
