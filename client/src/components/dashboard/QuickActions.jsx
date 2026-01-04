import { Link } from 'react-router-dom'
import { demoSession } from '../../state/demoSession'
import { Feature, canUseFeature } from '../../utils/accessControl'

const actions = [
  { title: 'Report Overdue Payer', to: '/defaulters', feature: Feature.REPORT_OVERDUE },
  { title: 'Add New PO', to: '/purchase-orders', feature: Feature.PO_MANAGEMENT },
  { title: 'View Defaulters', to: '/defaulters#status', feature: Feature.REPORT_OVERDUE },
  { title: 'Credit Reports', to: '/credit-reports', feature: Feature.CREDIT_REPORTS },
  { title: 'Settlement', to: '/settlement', feature: Feature.SETTLEMENT },
  { title: 'My Account', to: '/account' },
]

export default function QuickActions() {
  return (
    <div className="grid md:grid-cols-2 gap-4">
      {actions.map((item) => (
        <Link key={item.title} to={item.to} className="card hover:shadow-lg transition-shadow">
          <p className="font-heading font-semibold text-lg text-gray-900">{item.title}</p>
          <div className="flex items-center gap-2 mt-2 text-sm">
            <span className="text-primary-700">Go</span>
            {item.feature && !canUseFeature(demoSession, item.feature) && (
              <span className="text-amber-700 text-xs bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">Upgrade</span>
            )}
          </div>
        </Link>
      ))}
    </div>
  )
}
