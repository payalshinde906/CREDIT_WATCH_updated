import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Link } from 'react-router-dom'

const faqs = [
  {
    q: 'What services are included in CreditDataWatch\'s B2B Solutions?',
    a: 'CreditDataWatch\'s B2B Solutions cover tools such as company credit reports, auto payment reminders & follow-up, defaulter listing, business payment settlement, and risk benchmarking. These services help businesses manage credit relationships efficiently.',
  },
  {
    q: 'How can Auto Payment Reminders help in B2B transactions?',
    a: 'Auto payment reminders ensure that clients receive timely notifications about pending payments through SMS, email, or other channels. This minimizes delayed payments and supports smoother B2B cash flow.',
  },
  {
    q: 'Can I report a defaulter through CreditDataWatch\'s B2B Solutions?',
    a: 'Yes. Registered members can report MSMEs or other business entities that default on payments. Once verified, the defaulter gets listed, enabling other businesses to make informed decisions.',
  },
  {
    q: 'How does a Business Credit Report benefit B2B partnerships?',
    a: 'A Business Credit Report reveals a company\'s payment history, creditworthiness, and financial behavior. It helps in evaluating potential buyers or suppliers, reducing the risk of defaults and fostering trust in partnerships.',
  },
  {
    q: 'What is the process of settling payments from defaulters or buyers?',
    a: 'The settlement process involves listing the defaulter, initiating communication, negotiating terms, marking payments as settled, and optionally removing the name upon agreement. CreditDataWatch provides documentation tools and follow-ups to help members resolve dues.',
  },
]

export default function B2B() {
  const [openFaq, setOpenFaq] = useState(0)

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">

          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">B2B Solutions</h1>
            <p className="text-xl text-gray-600">Elevating Your Business with CreditDataWatch</p>
          </div>

          {/* Section 1: Unleashing the Power */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Unleashing the Power of B2B Solutions</h2>
            <h3 className="text-xl font-semibold text-gray-900">How CreditDataWatch's tailored B2B Solutions redefine the landscape</h3>
            <p className="text-gray-700 leading-relaxed">
              In today's competitive business environment, having robust and efficient B2B solutions is essential for the success and growth of any organization. CreditDataWatch, a leading provider of credit information and risk management services, offers a range of tailored B2B solutions that can redefine the landscape of your business.
            </p>
            <p className="text-gray-700 leading-relaxed">
              With CreditDataWatch's B2B solutions, you can unlock the power of data-driven decision making. By providing comprehensive and accurate credit information, CreditDataWatch enables businesses to make informed choices about their partners, suppliers, and customers. Whether it's assessing the creditworthiness of a potential client or managing the credit risks associated with your existing customers, CreditDataWatch's B2B solutions can help you navigate the complex world of business credit.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch's B2B solutions are designed to streamline and automate your credit management processes. By leveraging advanced technology and analytics, CreditDataWatch enables businesses to efficiently manage credit checks, credit scoring, and credit monitoring. This not only saves time and effort but also minimizes the risk of financial losses due to defaults or late payments.
            </p>
          </div>

          {/* Section 2: Excellence in B2B Service */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Excellence in B2B Service</h2>
            <p className="text-gray-700 leading-relaxed">
              When it comes to B2B service, CreditDataWatch stands out from the crowd. With a relentless commitment to excellence, CreditDataWatch ensures that its clients receive the highest level of service and support. From the moment you engage with CreditDataWatch, you can expect personalized attention and a dedicated team of experts who will go the extra mile to meet your unique business needs.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch understands that every business is different and requires tailored solutions. That's why their team of professionals takes the time to understand your specific requirements and design B2B solutions that align with your goals and objectives. Whether you need assistance with credit risk management, debt solutions, or accessing commercial CREDIT reports online, CreditDataWatch has the expertise and experience to deliver outstanding results.
            </p>
          </div>

          {/* Section 3: Strategic Business Credit Solutions */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Strategic Business Credit Solutions</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch's strategic business credit solutions are designed to empower your organization and help you achieve your goals. Whether you are a small business or a large corporation, CreditDataWatch has the expertise and resources to support your credit management needs.
            </p>
            <p className="text-gray-700 leading-relaxed">
              One of CreditDataWatch's key offerings is their B2B credit risk management services. By leveraging advanced algorithms and predictive analytics, CreditDataWatch's credit risk management services can help you identify potential risks and take proactive measures to mitigate them. From assessing the creditworthiness of your customers to monitoring their payment behavior, CreditDataWatch's credit risk management services provide you with the insights you need to make informed decisions and protect your business's health.
            </p>
          </div>

          {/* Section 4: Elevating Business Credit Management */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Elevating Business Credit Management</h2>
            <p className="text-gray-700 leading-relaxed">
              One of the key features of CreditDataWatch's B2B credit risk management services is their comprehensive credit assessment process. CreditDataWatch utilizes a combination of traditional credit scoring models, industry-specific data, and advanced analytics to evaluate the creditworthiness of your customers. This enables you to make informed decisions about extending credit and setting appropriate credit limits.
            </p>
            <p className="text-gray-700 leading-relaxed">
              In addition to performing rigorous credit assessments and monitoring, CreditDataWatch also facilitates professional debt settlement services. If you have customers who have defaulted on their payments, CreditDataWatch can assist you in settling the outstanding debt, helping you navigate the complex world of business credit with confidence.
            </p>
          </div>

          {/* Section 5: No Defaulters Policy */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">No Defaulters – Ensuring Business Credit Health</h2>
            <p className="text-gray-700 leading-relaxed">
              One of the biggest challenges businesses face when extending credit to their customers is the risk of defaults. Defaults can have a significant impact on your business's cash flow. That's why CreditDataWatch has implemented a strict "No Defaulters" policy to ensure the credit health of your business.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch's "No Defaulters" policy means that they have a zero-tolerance approach towards defaulting customers. By leveraging their extensive database and credit risk assessment models, CreditDataWatch can identify potential defaulters and alert you before extending credit. This proactive approach helps you avoid bad debts and minimize the risk of financial losses.
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
            <h3 className="text-2xl font-heading font-bold text-primary-900">Get Started with CreditDataWatch</h3>
            <p className="text-gray-700">Ready to elevate your business with tailored B2B solutions? Schedule an appointment today!</p>
            <Link to="/appointment" className="btn-primary inline-block">
              Book Appointment
            </Link>
          </div>

        </motion.div>
      </div>
    </section>
  )
}
