import { Link } from 'react-router-dom'
import { useAuth } from '../../state/authContext'

const actions = [
  { emoji: '📋', label: 'Report Overdue Payer', to: '/defaulters', feature: 'REPORT_OVERDUE' },
  { emoji: '👥', label: 'View Defaulters', to: '/defaulters#status', feature: 'REPORT_OVERDUE' },
  { emoji: '📊', label: 'Credit Reports', to: '/credit-reports', feature: 'CREDIT_REPORTS' },
  { emoji: '🤝', label: 'Settlement', to: '/settlement', feature: 'SETTLEMENT' },
]

export default function QuickActions() {
  const { canAccessFeature, user } = useAuth()
  const role = String(user?.role || '').toUpperCase()
  const isMasterAdmin = role === 'MASTER_ADMIN'
  const allActions = [
    ...actions,
    ...(role === 'MASTER_ADMIN' || role === 'COMPANY_ADMIN' ? [{ emoji: '👤', label: 'Team Management', to: '/admin/team' }] : []),
  ]
  return (
    <div className="flex flex-wrap gap-4">
      {allActions.map((item) => (
        <Link 
          key={item.label} 
          to={item.to} 
          className="flex items-center gap-3 px-5 py-3 rounded-xl border-2 border-primary-100 bg-primary-50 shadow-md hover:shadow-lg hover:border-primary-400 hover:bg-white transition-all text-base font-bold text-primary-900 group"
        >
          <span className="text-xl group-hover:scale-110 transition-transform">{item.emoji}</span>
          <span>{item.label}</span>
          {item.feature && !isMasterAdmin && !canAccessFeature(item.feature) && (
            <span className="text-[11px] font-semibold bg-amber-100 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
              Upgrade
            </span>
          )}
        </Link>
      ))}
    </div>
  )
}
