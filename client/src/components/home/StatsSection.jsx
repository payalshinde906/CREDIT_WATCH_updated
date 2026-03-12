import { motion } from 'framer-motion'

const stats = [
  { label: 'Highest No. of Defaulters by a Single Customer', value: '668+', color: 'text-white' },
  { label: 'Total Number of MSMEs Connected', value: '39+ Lakhs', color: 'text-white' },
  { label: 'Average Percentage of Settlements', value: '59%', color: 'text-white' },
  { label: 'Total amount reported defaulter', value: '4578+ Crores', color: 'text-white' },
]

export default function StatsSection() {
  return (
    <section className="section-padding bg-primary-700 text-white">
      <div className="container-custom">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-heading font-bold mb-2">CreditDataWatch: The Stats Behind the Trust</h2>
          <p className="text-primary-100">Numbers updated periodically as backend integrations go live.</p>
        </div>
        <div className="grid gap-6 grid-cols-2 md:grid-cols-4">
          {stats.map((stat, idx) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              className="card bg-white/10 border border-white/10 text-center"
            >
              <p className="text-3xl md:text-4xl font-heading font-bold">{stat.value}</p>
              <p className="mt-2 text-sm text-primary-100">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
