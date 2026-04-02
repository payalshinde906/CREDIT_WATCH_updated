import { useMemo, useEffect, useState } from 'react'
import QuickActions from '../components/dashboard/QuickActions'
import NotificationsPanel from '../components/dashboard/NotificationsPanel'
import { useAuth } from '../state/authContext'
import { purchaseOrders, invoices, defaulters, creditReports, settlements, appointments, wallet, adminApi } from '../services/api/apiClient'
import { Link } from 'react-router-dom'
import EditPOModal from '../components/po/EditPOModal'
import PurchaseOrders from './PurchaseOrders'

export default function Dashboard() {
  const { user, subscription, loading } = useAuth()
  const [stats, setStats] = useState({
    purchaseOrders: 0,
    invoices: 0,
    defaulters: 0,
    creditReports: 0,
    settlements: 0,
    appointments: 0,
    wallet: 0,
  })
  const [recentActivity, setRecentActivity] = useState([])
  const [dueReminders, setDueReminders] = useState([])
  const [loadingData, setLoadingData] = useState(true)
  const [purchaseRows, setPurchaseRows] = useState([])
  const [purchaseLoading, setPurchaseLoading] = useState(false)
  const [editingPO, setEditingPO] = useState(null)
  const [invitations, setInvitations] = useState([])
  const [invLoading, setInvLoading] = useState(false)
  const [invMessage, setInvMessage] = useState('')
  const [invForm, setInvForm] = useState({ email: '', role: 'OPERATIONS', expiry_hours: 24 })

  useEffect(() => {
    if (user) {
      fetchDashboardData()
      loadPurchaseHistory()
    }
  }, [user])

  useEffect(() => {
    const email = String(user?.email || '').toLowerCase()
    const isAdmin = String(user?.role || '').toLowerCase() === 'admin' || email === 'payalshinde906@gmail.com'
    if (user && isAdmin) {
      (async () => {
        setInvLoading(true)
        const res = await adminApi.listInvitations()
        if (res.ok && Array.isArray(res.data)) {
          setInvitations(res.data)
        }
        setInvLoading(false)
      })()
    }
  }, [user])

  const handleInviteSubmit = async (e) => {
    e.preventDefault()
    setInvMessage('')
    const hours = Number(invForm.expiry_hours)
    if (!invForm.email || !invForm.role) {
      setInvMessage('Email and role are required')
      return
    }
    if (Number.isNaN(hours) || hours < 1 || hours > 168) {
      setInvMessage('Expiry must be between 1 and 168 hours')
      return
    }
    const res = await adminApi.createInvitation({ email: invForm.email, role: invForm.role, expiry_hours: hours })
    if (res.ok) {
      setInvMessage(`Invitation created. Token: ${res.data?.token}`)
      setInvForm({ email: '', role: 'OPERATIONS', expiry_hours: 24 })
      const listRes = await adminApi.listInvitations()
      if (listRes.ok && Array.isArray(listRes.data)) {
        setInvitations(listRes.data)
      }
    } else {
      setInvMessage(res.error || 'Failed to create invitation')
    }
  }

  const calculateDaysLeft = (dueDateStr, paymentWindowDays = 0) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const dueDate = new Date(dueDateStr)
    dueDate.setHours(0, 0, 0, 0)
    
    // Add payment window days to due date
    const effectiveDueDate = new Date(dueDate)
    effectiveDueDate.setDate(effectiveDueDate.getDate() + parseInt(paymentWindowDays || 0))
    
    const daysLeft = Math.floor((effectiveDueDate - today) / (1000 * 60 * 60 * 24))
    return daysLeft
  }

  const fetchDashboardData = async () => {
    setLoadingData(true)
    try {
      const [posRes, invoicesRes, defaultersRes, reportsRes, settlementsRes, appointmentsRes, remindersRes, walletRes] = await Promise.all([
        purchaseOrders.list(1, 10, false),
        invoices.list({ limit: 10 }),
        defaulters.list(1, 10),
        creditReports.list(1, 10),
        settlements.list(1, 10),
        appointments.list(),
        invoices.getDueReminders(),
        wallet.getBalance(),
      ])

      // Set stats
      setStats({
        purchaseOrders: posRes.ok ? (Array.isArray(posRes.data) ? posRes.data.length : (posRes.data?.items?.length || 0)) : 0,
        invoices: invoicesRes.ok ? (Array.isArray(invoicesRes.data) ? invoicesRes.data.length : (invoicesRes.data?.invoices?.length || 0)) : 0,
        defaulters: defaultersRes.ok ? (Array.isArray(defaultersRes.data) ? defaultersRes.data.length : (defaultersRes.data?.items?.length || 0)) : 0,
        creditReports: reportsRes.ok ? (Array.isArray(reportsRes.data) ? reportsRes.data.length : (reportsRes.data?.items?.length || 0)) : 0,
        settlements: settlementsRes.ok ? (Array.isArray(settlementsRes.data) ? settlementsRes.data.length : (settlementsRes.data?.items?.length || 0)) : 0,
        appointments: appointmentsRes.ok ? (Array.isArray(appointmentsRes.data) ? appointmentsRes.data.length : 0) : 0,
        wallet: walletRes.ok ? (walletRes.data?.balance || 0) : 0,
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

  const loadPurchaseHistory = async () => {
    setPurchaseLoading(true)
    const res = await purchaseOrders.list(1, 100, true)
    if (res.ok && Array.isArray(res.data?.items)) {
      setPurchaseRows(res.data.items)
    } else if (res.ok && Array.isArray(res.data)) {
      setPurchaseRows(res.data)
    } else {
      setPurchaseRows([])
    }
    setPurchaseLoading(false)
  }

  const handleArchivePO = async (po) => {
    const res = await purchaseOrders.archive(po.id)
    if (res.ok) {
      setPurchaseRows((prev) => prev.map(r => r.id === po.id ? { ...r, is_archived: !r.is_archived } : r))
    }
  }

  const handleDeletePO = async (po) => {
    const res = await purchaseOrders.delete(po.id)
    if (res.ok) {
      setPurchaseRows((prev) => prev.filter(r => r.id !== po.id))
    }
  }

  const handleSaveEditPO = async (payload) => {
    if (!editingPO) return false
    const res = await purchaseOrders.update(editingPO.id, payload)
    if (res.ok) {
      setPurchaseRows((prev) => prev.map(r => r.id === editingPO.id ? { ...r, ...payload } : r))
      return true
    }
    return false
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
    <section className="py-8 md:py-12">
      <div className="container-custom space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col gap-1">
            <p className="text-xs text-gray-500">
              {loading ? 'Loading profile...' : `Welcome back, ${user?.company_name || user?.email || 'Member'}`}
            </p>
            <h1 className="text-2xl font-heading font-bold text-gray-900">Dashboard</h1>
          </div>
          
          {/* My Wallet - Slim Inline Strip */}
          <div className="flex items-center gap-3 px-4 py-2 bg-indigo-50/50 border border-indigo-100 rounded-full">
            <span className="text-xs font-medium text-indigo-700 flex items-center gap-1.5">
              💳 Wallet: <span className="font-bold">{stats.wallet}</span> pts
            </span>
            <Link to="/wallet" className="text-[11px] font-semibold text-indigo-600 hover:underline">
              Redeem →
            </Link>
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border-2 border-blue-500 shadow-sm bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Purchase Orders</p>
              <Link to="/purchase-orders" className="text-xs text-blue-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-blue-600">{stats.purchaseOrders}</p>
          </div>
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-green-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Invoices</p>
              <Link to="/invoices" className="text-xs text-green-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-green-600">{stats.invoices}</p>
          </div>
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-red-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Defaulters</p>
              <Link to="/defaulters" className="text-xs text-red-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-red-600">{stats.defaulters}</p>
          </div>
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-purple-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Credit Reports</p>
              <Link to="/credit-reports" className="text-xs text-purple-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-purple-600">{stats.creditReports}</p>
          </div>
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-teal-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Settlements</p>
              <Link to="/settlement" className="text-xs text-teal-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-teal-600">{stats.settlements}</p>
          </div>
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-orange-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex flex-col">
              <p className="text-xs text-gray-500">Appointments</p>
              <Link to="/appointment" className="text-xs text-orange-600 hover:underline inline-block">
                View all →
              </Link>
            </div>
            <p className="text-2xl font-bold text-orange-600">{stats.appointments}</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-3">
          <h2 className="text-base font-bold text-gray-700 uppercase tracking-wide mb-3">Quick Actions</h2>
          <QuickActions />
        </div>

        {/* Smaller Dashboard Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          {/* Recent Activity */}
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-blue-200 shadow-sm border-l-4 border-l-blue-400 bg-white hover:shadow-md transition-shadow">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm">🕐</span>
                <h2 className="text-xs text-gray-500 uppercase font-semibold">Recent Activity</h2>
              </div>
              {loadingData && (
                <p className="text-xs text-gray-500">Loading activity...</p>
              )}
              {!loadingData && recentActivity.length === 0 && (
                <p className="text-xs text-gray-500 py-1">No recent activity</p>
              )}
              {!loadingData && recentActivity.length > 0 && (
                <div className="space-y-1 overflow-y-auto max-h-24 pr-1">
                  {recentActivity.slice(0, 3).map((activity) => (
                    <Link
                      key={`${activity.type}-${activity.title}`}
                      to={activity.link}
                      className="flex items-start gap-2 p-1 rounded hover:bg-gray-50 transition-colors"
                    >
                      <span className="text-sm">{getActivityIcon(activity.type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-[10px] font-semibold text-gray-900 truncate">{activity.title}</p>
                        <p className="text-[9px] text-gray-600 truncate">{activity.description}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Due Reminders */}
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-orange-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm">🔔</span>
                <h2 className="text-xs text-gray-500 uppercase font-semibold">Due Reminders</h2>
              </div>
              {loadingData && (
                <p className="text-xs text-gray-500">Loading...</p>
              )}
              {!loadingData && dueReminders.length === 0 && (
                <p className="text-xs text-gray-500 py-1">No reminders due</p>
              )}
              {!loadingData && dueReminders.length > 0 && (
                <div className="space-y-1 overflow-y-auto max-h-24 pr-1">
                  {dueReminders.slice(0, 2).map((invoice) => (
                    <div key={invoice.id} className="p-1 bg-orange-50/50 border border-orange-100 rounded">
                      <p className="text-[10px] font-semibold text-gray-900 truncate">{invoice.invoice_number}</p>
                      <div className="flex justify-between items-center mt-0.5">
                        <p className="text-[9px] font-bold text-orange-800">
                          {formatCurrency(invoice.amount)}
                        </p>
                        <p className="text-[8px] text-gray-500">Due: {formatDate(invoice.due_date)}</p>
                      </div>
                    </div>
                  ))}
                  <Link
                    to="/invoices"
                    className="text-[9px] text-blue-600 hover:underline inline-block"
                  >
                    View all →
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Notifications */}
          <NotificationsPanel dueReminders={dueReminders} />

          {/* Plan Info */}
          <div className="flex items-center gap-4 px-5 py-3 rounded-xl border border-gray-100 shadow-sm border-l-4 border-purple-500 bg-white hover:shadow-md transition-shadow">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm">💳</span>
                <h2 className="text-xs text-gray-500 uppercase font-semibold">Subscription</h2>
              </div>
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium text-gray-700">{planLabel}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${subscription?.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {planStatus}
                  </span>
                </div>
                <Link to="/membership" className="inline-flex items-center justify-center bg-gray-50 border border-gray-200 text-gray-700 py-1 rounded text-[10px] font-semibold hover:bg-gray-100 transition-colors">
                  Manage Plan
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div>
          <PurchaseOrders />
        </div>

        {editingPO && (
          <EditPOModal
            po={editingPO}
            onClose={() => setEditingPO(null)}
            onSave={handleSaveEditPO}
          />
        )}
      </div>
    </section>
  )
}
