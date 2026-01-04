import MembershipPlans from '../components/membership/MembershipPlans'
import { demoSession } from '../state/demoSession'

export default function Membership() {
  return (
    <section className="section-padding">
      <div className="container-custom space-y-8">
        <div className="space-y-2">
          <p className="text-sm text-gray-500">GST-linked access control</p>
          <h1 className="text-3xl font-heading font-bold text-gray-900">Membership & Subscriptions</h1>
          <p className="text-gray-600 max-w-3xl">
            Choose a plan that unlocks overdue reporting, PO management, credit reports, and settlement workflows. Payments are stubbed for now; plans will sync from backend later.
          </p>
          <div className="rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-700 bg-white shadow-sm">
            <p className="font-semibold">Current plan (demo)</p>
            <p>{demoSession.subscription.plan.toUpperCase()} — Active</p>
          </div>
        </div>

        <MembershipPlans />

        <div className="card text-sm text-gray-700 space-y-2">
          <p className="font-semibold">What gets enforced?</p>
          <ul className="list-disc list-inside space-y-1">
            <li>GST validation and revalidation</li>
            <li>Feature gating for overdue reports, credit reports, POs, and settlements</li>
            <li>Usage limits per plan (to be enforced server-side)</li>
          </ul>
        </div>
      </div>
    </section>
  )
}
