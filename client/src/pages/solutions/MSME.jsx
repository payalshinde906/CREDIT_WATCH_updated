import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Link } from 'react-router-dom'

const faqs = [
  {
    q: 'What is included in the MSMEs Credit Report provided by CreditDataWatch?',
    a: 'It includes credit behavior trends, repayment history, credit health metrics, and insights into MSME risk levels, helping businesses make informed decisions.',
  },
  {
    q: 'How can I handle MSMEs Payment Defaulter effectively?',
    a: 'CreditDataWatch provides detailed insights on MSMEs Payment Defaulter, allowing registered members to monitor defaulters, take proactive steps, and manage credit risk efficiently.',
  },
  {
    q: 'Why is maintaining a good MSMEs Credit score important for business success?',
    a: 'A strong score improves credibility, helps attract partnerships and contracts, and enhances access to government benefits and preferential treatment.',
  },
  {
    q: 'What advantages do MSMEs receive through CreditDataWatch\'s support?',
    a: 'MSMEs benefit from improved credibility, data insights, simplified registration, and better positioning in business networks due to accurate credit assessments.',
  },
  {
    q: 'How can businesses report MSMEs Payment Defaulter using CreditDataWatch?',
    a: 'Businesses can report MSMEs Payment Defaulter via CreditDataWatch\'s platform, helping create transparency and enabling other members to make informed credit decisions.',
  },
]

export default function MSME() {
  const [openFaq, setOpenFaq] = useState(0)

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">

          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">MSME Solutions</h1>
            <p className="text-xl text-gray-600">Empowering MSMEs with CreditDataWatch</p>
          </div>

          {/* Section 1: Unleashing Potential */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Unleashing the Potential: Benefits of MSME in India</h2>
            <p className="text-gray-700 leading-relaxed">
              India's Micro, Small, and Medium Enterprises (MSMEs) sector has emerged as a vital contributor to the country's economic growth. With over 63 million registered MSMEs, this sector plays a crucial role in employment generation, innovation, and exports. MSMEs contribute around 30% to India's GDP, making them a significant driving force for economic development.
            </p>
            <p className="text-gray-700 leading-relaxed">
              The government of India recognizes the importance of MSMEs and has implemented several initiatives to support their growth. These include simplified registration processes, access to credit, and enabling technological advancements. MSMEs enjoy various benefits, such as subsidized loans, tax incentives, and preferential treatment in government procurement. These measures provide a favorable ecosystem for MSMEs to thrive and contribute to India's economic prosperity.
            </p>
          </div>

          {/* Section 2: Navigating MSME Credit Report */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Navigating the MSME Credit Report</h2>
            <p className="text-gray-700 leading-relaxed">
              Understanding the pulse of the MSMEs sector is crucial for policymakers, and other stakeholders. The MSMEs Credit Report provides valuable insights into the performance and credit behavior of MSMEs in India. This report analyzes the credit health of the sector. It highlights trends, challenges, and opportunities for MSMEs, helping them make informed decisions.
            </p>
          </div>

          {/* Section 3: MSME Registration Services */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">MSME Registration Services – Simplifying the Process</h2>
            <p className="text-gray-700 leading-relaxed">
              Registering as an MSMEs is the first step towards availing the benefits and support provided by the government. However, the registration process can be complex and time-consuming. This is where CreditDataWatch's MSME registration services come into play. With their streamlined processes and expertise in MSME registration, CreditDataWatch simplifies the journey for entrepreneurs.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch's MSMEs registration services eliminate the need for navigating through multiple government portals and paperwork. We provide a user-friendly interface that guides users through the registration process, ensuring compliance with all necessary requirements. By leveraging technology and automation, CreditDataWatch reduces the time and effort involved in MSME registration, allowing entrepreneurs to focus on their core business activities.
            </p>
          </div>

          {/* Section 4: Streamlining Registration Process */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">How CreditDataWatch’s MSME registration services streamline the registration process</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch’s MSME registration services offer a seamless experience for entrepreneurs looking to register their businesses. The platform provides step-by-step guidance, ensuring that all mandatory fields are filled accurately. It also offers real-time validation checks, minimizing errors and rework. CreditDataWatch’s automated system generates the necessary documents and forms, saving time and effort.
            </p>
            <p className="text-gray-700 leading-relaxed">
              Moreover, CreditDataWatch’s MSME registration services enable entrepreneurs to track the progress of their application. Users receive regular updates and notifications, keeping them informed about the status of their registration. This transparency and visibility instill confidence and trust in the process, making it easier for entrepreneurs to navigate the complexities of MSMEs registration.
            </p>
          </div>

          {/* Section 5: Significance of MSME Credit Score */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">The significance of MSME Credit score for business success</h2>
            <p className="text-gray-700 leading-relaxed">
              Creditworthiness is a crucial factor in accessing credit and other financial services. For MSMEs, having a good credit score is essential for business success. The MSMEs Credit score, provided by CreditDataWatch, assesses the creditworthiness of MSMEs based on their credit behavior and repayment history. A good credit score also enhances the credibility and reputation of an MSME, opening up opportunities for partnerships, collaborations, and contracts.
            </p>
          </div>

          {/* Section 6: Leveraging MSME Advantages */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Leveraging MSME advantages through CreditDataWatch</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch offers a range of solutions that empower MSMEs to leverage their advantages and maximize their potential. With their expertise in credit assessment and risk management, CreditDataWatch helps MSMEs unlock opportunities for growth and expansion. By utilizing CreditDataWatch’s services, MSMEs can:
            </p>
            <ul className="list-disc pl-5 text-gray-700 space-y-2">
              <li><strong>Access credit:</strong> CreditDataWatch’s comprehensive credit assessment enables MSMEs to demonstrate their creditworthiness, making it easier to secure loans and financial support.</li>
              <li><strong>Build credibility:</strong> A strong credit profile enhances the credibility of an MSMEs, attracting investors and business partners.</li>
            </ul>
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
            <h3 className="text-2xl font-heading font-bold text-primary-900">Explore MSME Solutions</h3>
            <p className="text-gray-700">Ready to boost your business credibility? Schedule an appointment today!</p>
            <Link to="/appointment" className="btn-primary inline-block">
              Book Appointment
            </Link>
          </div>

        </motion.div>
      </div>
    </section>
  )
}
