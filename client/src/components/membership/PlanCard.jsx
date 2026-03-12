import { motion } from 'framer-motion'
import PropTypes from 'prop-types'

export default function PlanCard({ plan, onSelect }) {
  const formatPrice = (price) => {
    if (price === 0) return 'Free'
    return `₹${price.toLocaleString('en-IN')}`
  }

  const formatValidity = (days) => {
    if (days === 365) return '1 Year'
    if (days === 180) return '6 Months'
    if (days === 30) return '1 Month'
    return `${days} Days`
  }

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      className="card h-full border border-gray-100"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xl font-heading font-semibold text-gray-900">{plan.display_name}</h3>
        <span className="text-xs px-2 py-1 rounded-full bg-primary-50 text-primary-700 font-semibold">
          {formatValidity(plan.validity_days)}
        </span>
      </div>
      <p className="text-3xl font-heading font-bold text-gray-900 mb-2">{formatPrice(plan.price)}</p>
      <p className="text-xs text-gray-600 mb-3">{plan.description}</p>
      <ul className="text-sm text-gray-700 space-y-2 mb-4">
        <li className="flex items-start gap-2">
          <span className="text-primary-600">✓</span>
          <span>Validity: {formatValidity(plan.validity_days)}</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="text-primary-600">✓</span>
          <span>CIR Generation: {plan.cir_generation_fee || 'Included'}</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="text-primary-600">✓</span>
          <span>Legal Assistance: {plan.legal_assistance || plan.legal_assistance_limit || 'NO'}</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="text-primary-600">✓</span>
          <span>Reminder Follow-ups: {plan.reminder_followups || 'Yes'}</span>
        </li>
      </ul>
      <button className="btn-primary w-full" onClick={() => onSelect(plan)}>
        Choose Plan
      </button>
    </motion.div>
  )
}

PlanCard.propTypes = {
  plan: PropTypes.shape({
    id: PropTypes.string.isRequired,
    display_name: PropTypes.string.isRequired,
    validity_days: PropTypes.number.isRequired,
    price: PropTypes.number.isRequired,
    follow_up_limit: PropTypes.number,
    legal_assistance_limit: PropTypes.number,
    description: PropTypes.string,
    cir_generation_fee: PropTypes.string,
    legal_assistance: PropTypes.string,
    reminder_followups: PropTypes.string,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
}
