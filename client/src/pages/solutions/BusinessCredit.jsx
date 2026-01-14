import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Link } from 'react-router-dom'

const faqs = [
  {
    q: 'What is CreditDataWatch\'s Business Credit Bureau?',
    a: 'CreditDataWatch\'s Business Credit Bureau is India\'s first platform dedicated to providing comprehensive credit information and management services for businesses. It enables suppliers and buyers to initiate transactions, receive acknowledgments, and report defaulters, thereby enhancing transparency and trust in business dealings.',
  },
  {
    q: 'How can I report a payment defaulter through CreditDataWatch?',
    a: 'To report a defaulter, register on the CreditDataWatch platform using your GSTIN. Once registered, you can add details of the defaulting business, including transaction information and payment history. The reported defaulter will then be listed, alerting other businesses and helping prevent future payment issues.',
  },
  {
    q: 'What is the \'Auto Payment Reminder and Follow-up\' feature?',
    a: 'This feature automates the process of sending payment reminders to clients. It includes SMS, email, and WhatsApp notifications, reducing manual follow-up efforts and increasing the likelihood of timely payments. The system also tracks responses and escalates reminders as needed.',
  },
  {
    q: 'How does CreditDataWatch\'s Business Credit Bureau benefit my business?',
    a: 'By utilizing CreditDataWatch\'s services, businesses can: Access detailed credit information of potential clients and partners; Report and track payment defaulters; Automate payment reminders and follow-ups; Improve cash flow management; Enhance credibility and trust within the business ecosystem.',
  },
]

export default function BusinessCredit() {
  const [openFaq, setOpenFaq] = useState(0)

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">

          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">Business Credit</h1>
            <p className="text-xl text-gray-600">Smarter Credit Management with Auto Reminders</p>
          </div>

          {/* Section 1: Business Credit Bureau */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Business Credit Bureau with Auto Payment Reminder and Follow Up</h2>
            <p className="text-gray-700 leading-relaxed">
              Access to reliable credit data and effective payment reminder tools is paramount for good financial health in today's ever-evolving business landscape. Accordingly, CreditDataWatch presents smart credit reporting, risk analysis, auto payment reminder and follow up tools for businesses to facilitate on-time payments and minimize default.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch: Empowering Businesses with Smart Credit Insights.
            </p>
          </div>

          {/* Section 2: Detailed Company Credit Reports */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Get Clarity with Detailed Company Credit Reports</h2>
            <p className="text-gray-700 leading-relaxed">
              A complete company credit report shows the financial behavior of a company with respect to payment history, liabilities, and credit utilization. For suppliers and MSMEs, this can help in assessing the creditworthiness and avoiding risky dealings.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch boasts advanced reporting instruments by which records of MSMEs Payment Defaulter will be stored and build confidence in timed business payment settlement strategies.
            </p>
          </div>

          {/* Section 3: Managing Collections */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Managing Collections Using Automated Payment Reminder and Settlement Processes</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch's different intelligent solutions make smooth sailing for collecting receivable invoices, from sending a Payment Reminder to Settlement from Buyer initiation and all stages in between. Auto Payment Reminder and Follow Up equip businesses to automate follow-ups and resolve collections before they escalate.
            </p>
          </div>

          {/* Section 4: Your Partner */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">CreditDataWatch: Your Partner for Credit and Settlement Management</h2>
            <p className="text-gray-700 leading-relaxed">
              With CreditDataWatch, you don’t only get credit data; we give you a whole ecosystem to manage payments, track MSMEs Payment Defaulters, and settle dues efficiently. Whether you are a startup or an enterprise, our tools are tailored to:
            </p>
            <ul className="list-disc pl-5 text-gray-700 space-y-2">
              <li>Identify high-risk clients</li>
              <li>Trigger automatic payment reminders</li>
              <li>Quickly debtor payment settlement</li>
              <li>Point out areas you are lacking through report generation</li>
            </ul>
          </div>

          {/* Section 5: Defaulters Knocking */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Defaulters Knocking? CreditDataWatch Has Got Your Back</h2>
            <p className="text-gray-700 leading-relaxed">
              Late payments and failure to pay invoices slow your cash flow. Before you think of settling the udhaar or Udhaar Ko Kaise Settlement Karu, CreditDataWatch does not let you think because it has already marked the trend, the alerts, and even early business payment settlement. Wondering “Udhaar Ko Kaise Settlement Karu?” Our system provides practical, step-by-step solutions to resolve overdue payments.
            </p>
          </div>

          {/* Section 6: Keep it Simple */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Keep it Simple for MSME Credit Operations</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch offers MSME a host of instruments designed to solve problems that are always peculiar to them. From catching MSMEs Payment Defaulter to facilitating settlement from buyer, our platform was made for the actualization of financial control. Real-time data, risk signals, and auto-follow-ups all came together to make credit management so simple, yet impactful.
            </p>
          </div>

          {/* Section 7: Get Started */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Get Started with CreditDataWatch Today</h2>
            <p className="text-gray-700 leading-relaxed">
              Ready to secure receivables and gain control over business payments? With CreditDataWatch, you get:
            </p>
            <ul className="list-disc pl-5 text-gray-700 space-y-2">
              <li>Smart business credit report and financial indicators</li>
              <li>Automated payment reminder and follow-up features</li>
              <li>Help with settling udhaar or pending dues</li>
              <li>A powerful platform for credit and payment management</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              Get on board now and make wise financial decisions that foster growth in your business.
            </p>
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

          {/* CTA Section */}
          <div className="card bg-primary-50 border-primary-200 text-center space-y-4">
            <h3 className="text-2xl font-heading font-bold text-primary-900">Start Managing Credit Smartly</h3>
            <p className="text-gray-700">Schedule an appointment with us today!</p>
            <Link to="/appointment" className="btn-primary inline-block">
              Book Appointment
            </Link>
          </div>

        </motion.div>
      </div>
    </section>
  )
}
