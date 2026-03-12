import { useAuth } from '../../state/authContext'

export default function NotificationsPanel({ dueReminders = [] }) {
  const { subscription, getDaysRemaining } = useAuth()
  const notifications = []

  // Add subscription expiry notification
  if (subscription?.expiry_date) {
    const daysRemaining = getDaysRemaining()
    if (daysRemaining !== null) {
      if (daysRemaining <= 7 && daysRemaining > 0) {
        notifications.push({
          id: 'subscription-expiry',
          type: 'alert',
          text: `Membership expires in ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''}`,
          priority: 'high',
        })
      } else if (daysRemaining === 0) {
        notifications.push({
          id: 'subscription-expired',
          type: 'alert',
          text: 'Your membership has expired. Please renew to continue using all features.',
          priority: 'high',
        })
      }
    }
  }

  // Add due reminders notifications
  if (dueReminders && dueReminders.length > 0) {
    dueReminders.slice(0, 3).forEach((invoice, index) => {
      notifications.push({
        id: `reminder-${invoice.id || index}`,
        type: 'reminder',
        text: `Payment reminder: ${invoice.invoice_number || 'Invoice'} - ${invoice.counterparty_name || 'Counterparty'}`,
        priority: 'medium',
      })
    })
  }

  // If no notifications, show a helpful message
  if (notifications.length === 0) {
    return (
      <div className="card p-3 h-full">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-heading font-semibold">Notifications</h3>
        </div>
        <p className="text-xs text-gray-500">No new notifications</p>
      </div>
    )
  }

  return (
    <div className="card p-3 h-full">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-heading font-semibold">Notifications</h3>
        {notifications.length > 0 && (
          <span className="text-[10px] text-gray-500">{notifications.length} new</span>
        )}
      </div>
      <ul className="space-y-1.5">
        {notifications.map((item) => (
          <li
            key={item.id}
            className={`text-[11px] flex items-start gap-2 p-1.5 rounded-lg ${
              item.priority === 'high'
                ? 'bg-red-50 text-red-800 border border-red-100'
                : item.priority === 'medium'
                ? 'bg-yellow-50 text-yellow-800 border border-yellow-100'
                : 'text-gray-700'
            }`}
          >
            <span
              className={`mt-1 h-1.5 w-1.5 rounded-full flex-shrink-0 ${
                item.priority === 'high'
                  ? 'bg-red-600'
                  : item.priority === 'medium'
                  ? 'bg-yellow-600'
                  : 'bg-primary-600'
              }`}
            />
            <span className="flex-1 leading-tight">{item.text}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
