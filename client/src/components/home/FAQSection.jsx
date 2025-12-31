import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const faqs = [
  {
    q: 'What is a business credit score?',
    a: 'A composite indicator derived from trade history, payment punctuality, and statutory compliance. CreditDataWatch will surface bureau-grade insights alongside your verified trade lines.',
  },
  {
    q: 'Registration vs Subscription?',
    a: 'Registration (GST validation) is mandatory to access the platform. Subscription unlocks continued access, periodic reporting, analytics, and workflow automation.',
  },
  {
    q: 'Is GST mandatory?',
    a: 'Yes. Only GST-registered entities can use CreditDataWatch. GSTIN is validated during sign-up and periodically rechecked.',
  },
  {
    q: 'Best practices for faster collections?',
    a: 'File overdue invoices early, attach POs and delivery proofs, keep acknowledgement trails, and use structured reminder cadences instead of ad-hoc emails.',
  },
  {
    q: 'How do I register? (video)',
    a: 'Watch the 2-minute walkthrough on YouTube to see GST validation, overdue filing, and appointment booking. (Placeholder link: https://youtu.be/demo-creditdatawatch)',
  },
]

export default function FAQSection() {
  const [open, setOpen] = useState(0)

  return (
    <section className="section-padding">
      <div className="container-custom max-w-4xl">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-heading font-bold mb-3">Help & Education</h2>
          <p className="text-lg text-gray-600">Common questions about CreditDataWatch</p>
        </div>
        <div className="space-y-4">
          {faqs.map((item, idx) => (
            <button
              key={item.q}
              type="button"
              className="card cursor-pointer w-full text-left"
              onClick={() => setOpen(open === idx ? -1 : idx)}
              aria-expanded={open === idx}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-gray-900">{item.q}</p>
                </div>
                <svg
                  className={`h-5 w-5 text-primary-600 transition-transform ${open === idx ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <AnimatePresence initial={false}>
                {open === idx && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <p className="text-gray-700 mt-3 leading-relaxed">{item.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
