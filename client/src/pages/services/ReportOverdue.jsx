import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Link } from 'react-router-dom'

const faqs = [
  {
    q: 'Who is a defaulter buyer party?',
    a: 'A defaulter is a company, firm, or organization that does not fulfill its obligation of making payment to their suppliers. CreditDataWatch provides access to information about defaulters, offering accurate data based on submissions from our registered businesses having valid GST number.',
  },
  {
    q: 'What documents should we upload to verify a defaulter?',
    a: 'To prove that a party is a defaulter, you should upload the following documents: an up-to-date ledger for the defaulter and a Chartered Accountant\'s certificate with the UDIN number. Additionally, any other documents requested by CreditDataWatch may also be required.',
  },
  {
    q: 'We submitted the documents for the defaulters, but the defaulter hasn\'t been listed in our records yet?',
    a: 'Typically, this process takes up to 2 working days. If your defaulter is still not listed, you can track the status by going to Dashboard > Defaulters. For further assistance, please contact us at support@creditdatawatch.in.',
  },
  {
    q: 'I am a defaulter and have settled my payment with the party, why I am receiving follow-up for outstanding amount?',
    a: 'Please request the party that reported you as a defaulter to update the settlement. Once they update the information, your follow-up will be stopped immediately on CreditDataWatch portal.',
  },
  {
    q: 'Are there any charges to add a defaulter?',
    a: 'Adding a defaulter is easy and completely free for registered members of CreditDataWatch.',
  },
  {
    q: 'If a settlement has been made but is not reported on the CreditDataWatch platform by the reporting party, what should the defaulter do?',
    a: 'It is the responsibility of the reporting member to update CreditDataWatch about the settlement. If they fail to do so, the defaulter party should contact our support team at support@creditdatawatch.in for assistance.',
  },
  {
    q: 'What if the defaulter party does not have a GSTIN?',
    a: 'In this case, the defaulter can be reported using their PAN number.',
  },
]

export default function ReportOverdue() {
  const [openFaq, setOpenFaq] = useState(0)

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">
          
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-heading font-bold mb-4">Report Overdue Payer</h1>
            <p className="text-xl text-gray-600">Report Business Credit Defaulters, Payment Defaulters List, Commercial Credit Defaulters</p>
          </div>

          {/* Section 1: Business Credit Defaulters */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Business Credit Defaulters - Expose on National Platform</h2>
            <p className="text-gray-700 leading-relaxed">
              The process of reporting a defaulter is very easy and completely free for all the CreditDataWatch registered members. By reporting a defaulter, MSMEs and businesses not only help themselves, as the settlement option is available on CreditDataWatch portal but also make sure that others do not fall in the trap of habitual credit defaulter.
            </p>
            <p className="text-gray-700 leading-relaxed">
              The reported defaulter will be exposed all over India as the Credit Information Report and Credit Defaulters list will be available to all the members across India.
            </p>
          </div>

          {/* Section 2: Who can Report */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">Who can Report Business Credit Defaulter and how can it be done?</h2>
            <p className="text-gray-700 leading-relaxed">
              Businesses or MSMEs who have a valid GST registration number and registered as member on CreditDataWatch, can report a credit defaulter. Then, it is 100% checked and verified by CreditDataWatch's specialist, so that members can be rest assured that the defaulter list and information on CreditDataWatch portal is verified and genuine.
            </p>
            <p className="text-gray-700 leading-relaxed">
              The process of reporting a defaulter is very easy and absolutely FREE for all the registered members. The registered members need to fill in all the required fields on the portal, under the Report Defaulter section and its done.
            </p>
          </div>

          {/* Section 3: What information is needed */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">What information is needed to report a defaulter?</h2>
            <p className="text-gray-700 leading-relaxed">
              Vital information required to report some business as credit defaulter includes submission of the ledger of the defaulter party, a certificate of due amount by the chartered accountant (CA) with UDIN number and other required information.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch team analyses all the submissions and once it is checked by the experts, the information is updated on the defaulters list, on the CreditDataWatch portal.
            </p>
          </div>

          {/* Section 4: How are defaulters verified */}
          <div className="card space-y-4">
            <h2 className="text-2xl font-heading font-bold text-primary-700">How are defaulters verified?</h2>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch takes special care that genuine businesses are not listed as defaulter accidentally. CreditDataWatch follows standard procedure and makes sure that the name of the defaulter is checked and verified before it is reported to the list of the defaulters on the CreditDataWatch portal. Every reasonable precaution is taken to make sure that defaulters list is foolproof and remains always updated.
            </p>
            <p className="text-gray-700 leading-relaxed">
              CreditDataWatch lists defaulters identified and added by the registered members. However, if the concerned parties, the registered member and the defaulter agrees and settles the payment then the registered member could remove defaulter's name from the list of defaulters on CreditDataWatch.
            </p>
            <p className="text-gray-700 leading-relaxed">
              The payment settlement is strictly between the defaulter and the registered member and CreditDataWatch does not in any way have any say in it. It is the sole discretion and will of the registered member to ask for the removal of the defaulter name from the list.
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
            <h3 className="text-2xl font-heading font-bold text-primary-900">Ready to Begin?</h3>
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
