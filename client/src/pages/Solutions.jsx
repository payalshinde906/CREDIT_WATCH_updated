import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const solutions = [
  { title: 'B2B Solutions', to: '/solutions/b2b', summary: 'Enterprise-grade controls, workflows, and analytics for large supply chains.' },
  { title: 'MSME Solutions', to: '/solutions/msme', summary: 'Guided flows for smaller teams to file overdues and automate reminders.' },
  { title: 'Business Credit', to: '/solutions/business-credit', summary: 'Build and protect business credit scores with verified trade lines.' },
  { title: 'Business Debt', to: '/solutions/business-debt', summary: 'Manage obligations, restructure, and maintain compliance.' },
]

export default function Solutions() {
  return (
    <section className="section-padding">
      <div className="container-custom">
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-heading font-bold mb-3">Solutions</h1>
          <p className="text-lg text-gray-600">Tailored for GST-registered enterprises and MSMEs.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {solutions.map((solution, idx) => (
            <motion.div
              key={solution.title}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              className="card flex flex-col gap-3"
            >
              <h3 className="text-2xl font-heading font-semibold">{solution.title}</h3>
              <p className="text-gray-700 text-sm">{solution.summary}</p>
              <div className="flex gap-3">
                <Link to={solution.to} className="btn-primary">Explore</Link>
                <Link to="/appointment" className="btn-secondary">Book demo</Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
