import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

const faqs = [
  {
    q: 'What is Business Credit Management?',
    a: 'Business Credit Management involves the systematic process of managing credit transactions between buyers and suppliers. It includes initiating, acknowledging, and tracking credit transactions to ensure timely payments and minimize defaults. CreditDataWatch\'s platform integrates with accounting software to automate reminders, share invoices, and report defaulters, thereby enhancing cash flow and business credibility.',
  },
  {
    q: 'How does CreditDataWatch help in reducing payment defaults?',
    a: 'CreditDataWatch helps businesses reduce payment defaults by providing tools such as auto payment reminders, follow-ups, and defaulter reporting. Registered members can report non-payments, which impacts the defaulter\'s credit reputation. This encourages timely payments from buyers and helps businesses safeguard their cash flow.',
  },
  {
    q: 'What are the benefits of using CreditDataWatch\'s Business Credit Management services?',
    a: 'CreditDataWatch offers several advantages, including: Automated transaction tracking and reminders, Digital acknowledgment of credit transactions, Professional approach to credit management, Easy settlement of dues, Enhanced business credibility, Improved cash flow management. These features help businesses reduce the risk of defaults and maintain healthy financial relationships.',
  },
  {
    q: 'Can I report a defaulter without any documents?',
    a: 'Yes, if you\'re utilizing CreditDataWatch\'s Business Credit Management services and no complications have arisen with the party, you can report a defaulter without submitting documents. However, if issues have occurred, you will need to provide a ledger and a Chartered Accountant\'s certificate with the UDIN to proceed with the defaulter report.',
  },
  {
    q: 'How does CreditDataWatch\'s Business Credit Management impact my business credit score?',
    a: 'By utilizing CreditDataWatch\'s Credit Management services, your business maintains a positive payment history and demonstrates creditworthiness. Regular use of the platform, timely settlements, and proper documentation all contribute to building a strong credit profile for your business.',
  },
]

export default function CreditManagement() {
  const [openFaq, setOpenFaq] = useState(0)

  const benefits = [
    'Automated Notifications, no manpower involved',
    'Digital Acknowledgement of transactions',
    'Professional Approach',
    'Monitoring all credit transactions in one place',
    'Easy Settlements',
    'Save cost and time',
    'Expand the business without fear',
  ]

  const features = [
    'Auto acceptance to supplier party by buyer party',
    'Auto Sharing of Invoices',
    'Auto reminders to Buyer party before and after the due date for payment',
    'After the due date Report the defaulter without any hustle with acknowledgement',
    'Decrease its credibility and credit score on PAN India',
  ]

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">
          
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">Credit Management</h1>
            <p className="text-xl text-gray-600">Business Credit Management Services | Credit Management Techniques</p>
          </div>

          {/* Main Description */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Business Credit Management</h2>
            <p className="text-gray-700 leading-relaxed">
              The Business Credit Management feature helps CreditDataWatch customers to manage their credit transactions digitally. Most of the transactions between Buyers and Suppliers are on Credit which might later become a defaulted transaction.
            </p>
            <p className="text-gray-700 leading-relaxed">
              Hence to ensure that there is a minimum probability of someone not making a repayment either in terms of Payment or Material Delivery, Business Credit Management will serve the purpose. It is the initiation, acknowledgement and tracking of the transactions between Buyers and Suppliers.
            </p>
          </div>

          {/* How it Works */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">How does it work</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch integrates with the customer accounting software like Tally, Marg, ERP etc. and sends the acknowledgement, reminders to the buyer party. It takes follow-ups with the buyer party if they are not paying on time. After defaulting or delay in payments, the Supplier can report that business as a defaulter on PAN India which impacts its credit score and decrease its credibility too.
            </p>
          </div>

          {/* What BCM Provides */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Business Credit Management provides its customers:</h2>
            <div className="space-y-2">
              {features.map((feature) => (
                <div key={feature} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-primary-600 flex-shrink-0" />
                  <p className="text-gray-700">{feature}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Benefits */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Benefits from Business Credit Management:</h2>
            <div className="space-y-2">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-green-600 flex-shrink-0" />
                  <p className="text-gray-700">{benefit}</p>
                </div>
              ))}
            </div>
          </div>

          {/* FAQ Section */}
          <div className="space-y-4">
            <h2 className="text-3xl font-heading font-bold text-center mb-6">Commonly Asked Questions</h2>
            <div className="space-y-3">
              {faqs.map((item, idx) => (
                <button
                  key={item.q}
                  type="button"
                  className="card cursor-pointer w-full text-left"
                  onClick={() => setOpenFaq(openFaq === idx ? -1 : idx)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-semibold text-gray-900">{item.q}</p>
                    <svg
                      className={`h-5 w-5 text-primary-600 transition-transform flex-shrink-0 ${openFaq === idx ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  <AnimatePresence initial={false}>
                    {openFaq === idx && (
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

        </motion.div>
      </div>
    </section>
  )
}
