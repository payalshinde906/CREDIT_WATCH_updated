import { motion } from 'framer-motion'

const testimonials = [
  {
    name: 'Aarav Mehta',
    role: 'CFO, Bharat Manufacturing',
    quote:
      'Trade validations inside CreditDataWatch cut our dispute cycles by 40% and improved collections visibility across plants.',
  },
  {
    name: 'Nisha Rao',
    role: 'Founder, MSME Exporter',
    quote:
      'Overdue reporting plus structured reminders helped us recover stuck invoices without escalating to legal each time.',
  },
]

export default function Testimonial() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-heading font-bold">Customer Trust</h2>
          <p className="text-lg text-gray-600">Signals from early adopters</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {testimonials.map((item, idx) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.08 }}
              className="card"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-full bg-primary-100 text-primary-700 font-heading font-bold flex items-center justify-center">
                  {item.name.split(' ').map((p) => p[0]).join('').slice(0, 2)}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{item.name}</p>
                  <p className="text-sm text-gray-600">{item.role}</p>
                </div>
              </div>
              <p className="text-gray-700 leading-relaxed">“{item.quote}”</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
