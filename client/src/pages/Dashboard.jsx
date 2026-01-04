import { useMemo, useEffect, useState } from 'react'
import QuickActions from '../components/dashboard/QuickActions'
import NotificationsPanel from '../components/dashboard/NotificationsPanel'
import { useAuth } from '../state/authContext'
import { purchaseOrders, invoices, defaulters, creditReports, settlements, appointments } from '../services/api/apiClient'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { user, subscription, loading } = useAuth()
  const [stats, setStats] = useState({
    purchaseOrders: 0,
    invoices: 0,
    defaulters: 0,
    creditReports: 0,
    settlements: 0,
    appointments: 0,
  })
  const [recentActivity, setRecentActivity] = useState([])
  const [dueReminders, setDueReminders] = useState([])
  const [loadingData, setLoadingData] = useState(true)

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    setLoadingData(true)
    try {
      // Fetch counts and recent data in parallel
      const [posRes, invoicesRes, defaultersRes, reportsRes, settlementsRes, appointmentsRes, remindersRes] = await Promise.all([
        purchaseOrders.list(1, 10, false),
        invoices.list({ limit: 10 }),
        defaulters.list(1, 10),
        creditReports.list(1, 10),
        settlements.list(1, 10),
        appointments.list(),
        invoices.getDueReminders(),
      ])

      // Set stats
      setStats({
        purchaseOrders: posRes.ok ? (posRes.data?.total || posRes.data?.items?.length || 0) : 0,
        invoices: invoicesRes.ok ? (invoicesRes.data?.total || invoicesRes.data?.invoices?.length || 0) : 0,
        defaulters: defaultersRes.ok ? (defaultersRes.data?.total || defaultersRes.data?.items?.length || 0) : 0,
        creditReports: reportsRes.ok ? (reportsRes.data?.total || reportsRes.data?.items?.length || 0) : 0,
        settlements: settlementsRes.ok ? (settlementsRes.data?.total || settlementsRes.data?.items?.length || 0) : 0,
        appointments: appointmentsRes.ok ? (appointmentsRes.data?.length || 0) : 0,
      })

      // Build recent activity from all sources
      const activity = []
      
      if (posRes.ok && posRes.data?.items) {
        posRes.data.items.slice(0, 3).forEach(po => {
          activity.push({
            type: 'purchase_order',
            title: `PO: ${po.number}`,
            description: `${po.vendor_name} - ${new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(po.amount)}`,
            date: po.created_at,
            link: '/purchase-orders',
          })
        })
      }

      if (invoicesRes.ok && invoicesRes.data?.invoices) {
        invoicesRes.data.invoices.slice(0, 3).forEach(inv => {
          activity.push({
            type: 'invoice',
            title: `Invoice: ${inv.invoice_number}`,
            description: `${inv.counterparty_name} - ${new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(inv.amount)}`,
            date: inv.created_at,
            link: '/invoices',
          })
        })
      }

      if (defaultersRes.ok && defaultersRes.data?.items) {
        defaultersRes.data.items.slice(0, 2).forEach(def => {
          activity.push({
            type: 'defaulter',
            title: `Defaulter Case: ${def.business_name}`,
            description: `GSTIN: ${def.business_gstin}`,
            date: def.created_at,
            link: '/defaulters',
          })
        })
      }

      // Sort by date and take top 8
      activity.sort((a, b) => new Date(b.date) - new Date(a.date))
      setRecentActivity(activity.slice(0, 8))

      // Set due reminders
      if (remindersRes.ok && remindersRes.data?.invoices) {
        setDueReminders(remindersRes.data.invoices.slice(0, 5))
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
    setLoadingData(false)
  }

  const planLabel = useMemo(() => {
    if (!subscription) return 'Loading plan...'
    return subscription.plan ? subscription.plan.toUpperCase() : 'BASE'
  }, [subscription])

  const planStatus = useMemo(() => {
    if (!subscription) return 'Checking...'
    return subscription.is_active ? 'Active' : 'Inactive'
  }, [subscription])

  const getActivityIcon = (type) => {
    switch (type) {
      case 'purchase_order':
        return '📋'
      case 'invoice':
        return '💰'
      case 'defaulter':
        return '⚠️'
      case 'credit_report':
        return '📊'
      case 'settlement':
        return '✅'
      default:
        return '📄'
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <section className="section-padding">
      <div className="container-custom space-y-8">
        <div className="flex flex-col gap-2">
          <p className="text-sm text-gray-500">
            {loading ? 'Loading profile...' : `Welcome back, ${user?.company_name || user?.email || 'Member'}`}
          </p>
          <h1 className="text-3xl font-heading font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Access overdue reporting, POs, credit checks, and settlements.</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Purchase Orders</p>
            <p className="text-3xl font-heading font-bold text-blue-600">{stats.purchaseOrders}</p>
            <Link to="/purchase-orders" className="text-xs text-blue-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Invoices</p>
            <p className="text-3xl font-heading font-bold text-green-600">{stats.invoices}</p>
            <Link to="/invoices" className="text-xs text-green-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Defaulters</p>
            <p className="text-3xl font-heading font-bold text-red-600">{stats.defaulters}</p>
            <Link to="/defaulters" className="text-xs text-red-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Credit Reports</p>
            <p className="text-3xl font-heading font-bold text-purple-600">{stats.creditReports}</p>
            <Link to="/credit-reports" className="text-xs text-purple-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Settlements</p>
            <p className="text-3xl font-heading font-bold text-teal-600">{stats.settlements}</p>
            <Link to="/settlement" className="text-xs text-teal-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
          <div className="card hover:shadow-md transition-shadow">
            <p className="text-sm text-gray-500 mb-1">Appointments</p>
            <p className="text-3xl font-heading font-bold text-orange-600">{stats.appointments}</p>
            <Link to="/appointment" className="text-xs text-orange-600 hover:underline mt-2 inline-block">
              View all →
            </Link>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="card space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-heading font-semibold text-gray-900">Quick Actions</h2>
                <span className="text-sm text-gray-500">Jump to priority workflows</span>
              </div>
              <QuickActions />
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Recent Activity</h2>
              {loadingData && (
                <p className="text-gray-500">Loading activity...</p>
              )}
              {!loadingData && recentActivity.length === 0 && (
                <p className="text-gray-500">No recent activity</p>
              )}
              {!loadingData && recentActivity.length > 0 && (
                <div className="space-y-3">
                  {recentActivity.map((activity) => (
                    <Link
                      key={`${activity.type}-${activity.title}`}
                      to={activity.link}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <span className="text-2xl">{getActivityIcon(activity.type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate">{activity.title}</p>
                        <p className="text-xs text-gray-600 truncate">{activity.description}</p>
                        <p className="text-xs text-gray-400 mt-1">{formatDate(activity.date)}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            {/* Due Reminders */}
            <div className="card">
              <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Due Reminders</h2>
              {loadingData && (
                <p className="text-sm text-gray-500">Loading reminders...</p>
              )}
              {!loadingData && dueReminders.length === 0 && (
                <p className="text-sm text-gray-500">No reminders due</p>
              )}
              {!loadingData && dueReminders.length > 0 && (
                <div className="space-y-3">
                  {dueReminders.map((invoice) => (
                    <div key={invoice.id} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm font-semibold text-gray-900">{invoice.invoice_number}</p>
                      <p className="text-xs text-gray-600">{invoice.counterparty_name}</p>
                      <p className="text-sm font-bold text-yellow-800 mt-1">
                        {formatCurrency(invoice.amount)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Due: {formatDate(invoice.due_date)}</p>
                    </div>
                  ))}
                  <Link
                    to="/invoices"
                    className="text-sm text-blue-600 hover:underline inline-block"
                  >
                    View all invoices →
                  </Link>
                </div>
              )}
            </div>

            {/* Notifications */}
            <div className="card">
              <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Notifications</h2>
              <NotificationsPanel />
            </div>

            {/* Plan Info */}
            <div className="card space-y-2 text-sm text-gray-700">
              <p className="font-semibold">Subscription</p>
              <p>Current: {planLabel}</p>
              <p>Status: {planStatus}</p>
              <Link to="/membership" className="btn-secondary w-full text-center">
                Manage Plan
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
