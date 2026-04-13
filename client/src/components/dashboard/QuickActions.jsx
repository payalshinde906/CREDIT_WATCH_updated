import { Link } from 'react-router-dom'
import { useAuth } from '../../state/authContext'

const actions = [
  { 
    emoji: '📋', 
    label: 'Report Overdue Payer', 
    to: '/services/report-overdue', 
    feature: 'REPORT_OVERDUE',
    color: 'blue'
  },
  { 
    emoji: '👥', 
    label: 'View Defaulters', 
    to: '/defaulters', 
    feature: 'REPORT_OVERDUE',
    color: 'purple'
  },
  { 
    emoji: '📊', 
    label: 'Credit Reports', 
    to: '/credit-reports', 
    feature: 'CREDIT_REPORTS',
    color: 'teal'
  },
  { 
    emoji: '🤝', 
    label: 'Settlement', 
    to: '/settlement', 
    feature: 'SETTLEMENT',
    color: 'orange'
  },
]

export default function QuickActions() {
  const { canAccessFeature, user } = useAuth()
  const role = String(user?.role || '').toUpperCase()
  const isMasterAdmin = role === 'MASTER_ADMIN'
  const allActions = [
    ...actions,
    ...(role === 'MASTER_ADMIN' || role === 'COMPANY_ADMIN' ? [{ 
      emoji: '👤', 
      label: 'Team Management', 
      to: '/admin/team',
      color: 'indigo'
    }] : []),
  ]

  const colorMap = {
    blue: 'border-blue-100 bg-blue-50/50 text-blue-900 hover:border-blue-400',
    purple: 'border-purple-100 bg-purple-50/50 text-purple-900 hover:border-purple-400',
    teal: 'border-teal-100 bg-teal-50/50 text-teal-900 hover:border-teal-400',
    orange: 'border-orange-100 bg-orange-50/50 text-orange-900 hover:border-orange-400',
    indigo: 'border-indigo-100 bg-indigo-50/50 text-indigo-900 hover:border-indigo-400',
  }

  return (
    <div className="flex flex-wrap gap-4">
      {allActions.map((item) => (
        <Link 
          key={item.label} 
          to={item.to} 
          className={`flex items-center gap-3 px-5 py-3 rounded-xl border-2 shadow-sm hover:shadow-md hover:bg-white transition-all text-base font-bold group ${colorMap[item.color] || 'border-gray-100 bg-gray-50 text-gray-900'}`}
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
