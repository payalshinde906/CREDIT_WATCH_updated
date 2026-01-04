const sample = [
  { id: 1, type: 'reminder', text: 'Payment reminder scheduled for INV-2201 (Jan 14)' },
  { id: 2, type: 'followup', text: 'Follow-up sent to Acme Traders' },
  { id: 3, type: 'alert', text: 'Membership expires in 12 days' },
]

export default function NotificationsPanel() {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-heading font-semibold">Notifications</h3>
        <span className="text-xs text-gray-500">Sample data</span>
      </div>
      <ul className="space-y-2">
        {sample.map((item) => (
          <li key={item.id} className="text-sm text-gray-700 flex items-start gap-2">
            <span className="mt-1 h-2 w-2 rounded-full bg-primary-600" />
            <span>{item.text}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
