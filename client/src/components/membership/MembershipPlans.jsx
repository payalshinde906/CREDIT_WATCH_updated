import PlanCard from './PlanCard'
import { useState, useEffect } from 'react'
import SubscribeModal from './SubscribeModal'
import { api } from '../../services/api/apiClient'

export default function MembershipPlans() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true)
        const response = await api.get('/subscriptions/plans')

        if (response.ok && response.data) {
          setPlans(response.data)
          setError(null)
        } else {
          setError('Failed to load plans')
          // Fallback to default plans
          setPlans(getDefaultPlans())
        }
      } catch (err) {
        console.error('Error fetching plans:', err)
        // Fallback to default plans
        setPlans(getDefaultPlans())
      } finally {
        setLoading(false)
      }
    }

    fetchPlans()
  }, [])

  const getDefaultPlans = () => [
    {
      id: 'base',
      name: 'base',
      display_name: 'Base',
      price: 500,
      validity_days: 30,
      follow_up_limit: 999,
      legal_assistance: 'NO',
      reminder_followups: 'Yes',
      cir_generation_fee: 'Included',
      description: 'Entry-level plan for small businesses'
    },
    {
      id: 'royal',
      name: 'royal',
      display_name: 'Royal',
      price: 1000,
      validity_days: 180,
      follow_up_limit: 999,
      legal_assistance: '5 Incidents follow ups',
      reminder_followups: 'Yes',
      cir_generation_fee: 'Included',
      description: 'For growing businesses with legal support'
    },
    {
      id: 'groups',
      name: 'groups',
      display_name: 'Groups',
      price: 2000,
      validity_days: 365,
      follow_up_limit: 999,
      legal_assistance: '20 Incidents follow ups',
      reminder_followups: 'Yes',
      cir_generation_fee: 'Included',
      description: 'For organizations managing multiple business entities'
    },
    {
      id: 'enterprise',
      name: 'enterprise',
      display_name: 'Enterprise',
      price: 100000,
      validity_days: 365,
      follow_up_limit: 999,
      legal_assistance: '100 Incidents follow ups',
      reminder_followups: 'Yes',
      cir_generation_fee: 'Included',
      description: 'Enterprise solution with maximum legal assistance'
    },
  ]

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card h-full animate-pulse bg-gray-200"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 text-sm text-amber-800">
          {error} — Using default plans
        </div>
      )}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {plans.map((plan) => (
          <PlanCard key={plan.id} plan={plan} onSelect={setSelected} />
        ))}
      </div>
      <SubscribeModal plan={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
