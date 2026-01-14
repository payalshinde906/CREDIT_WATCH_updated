import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../state/authContext'

export default function Membership() {
  const { subscription, loading } = useAuth()

  // No local state needed if we use context subscription directly
  // But we can keep it if we want to add more logic later

  if (loading) return <div className="p-10 text-center">Loading membership details...</div>

  // If no subscription found (e.g. error), show fallback
  if (!subscription) {
    return <div className="p-10 text-center text-red-600">Failed to load subscription information.</div>
  }

  const planName = subscription.plan ? subscription.plan.toUpperCase() : 'UNKNOWN'
  const status = subscription.status || 'Active'
  // Calculate validity if possible, or show 'N/A'
  const validity = subscription.expiry_date ? new Date(subscription.expiry_date).toLocaleDateString() : 'Lifetime'

  return (
    <section className="section-padding">
      <div className="container-custom space-y-8">
        <div className="space-y-2">
          <p className="text-sm text-gray-500">My Account</p>
          <h1 className="text-3xl font-heading font-bold text-gray-900">Membership Status</h1>
          <p className="text-gray-600 max-w-3xl">
            Manage your current plan, view usage limits, and renew your subscription.
          </p>
        </div>

        <div className="card max-w-2xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-wide">Current Plan</p>
              <h2 className="text-2xl font-bold text-primary-700">{planName}</h2>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full uppercase">
              {status}
            </span>
          </div>

          <div className="space-y-4 border-t border-gray-100 pt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Status</span>
              <span className="font-medium text-gray-900">{status}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Valid Until</span>
              <span className="font-medium text-gray-900">{validity}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Usage Limits</span>
              <span className="font-medium text-gray-900">See Plan Details</span>
            </div>
          </div>

          <div className="mt-8 flex gap-4">
            <Link to="/offerings" className="btn-primary flex-1 text-center">
              Upgrade / Change Plan
            </Link>
            <button className="btn-secondary flex-1" disabled>
              Cancel Subscription
            </button>
          </div>
        </div>

        <div className="card max-w-2xl bg-blue-50 border-blue-100">
          <h3 className="font-semibold text-blue-900 mb-2">Need more capabilities?</h3>
          <p className="text-sm text-blue-800 mb-4">
            Upgrade to our **Royal** or **Groups** plans to unlock legal assistance, more monthly reports, and API access.
          </p>
          <Link to="/offerings" className="text-blue-700 font-semibold text-sm hover:underline">
            View all offerings &rarr;
          </Link>
        </div>
      </div>
    </section>
  )
}
