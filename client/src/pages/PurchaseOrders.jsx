import { useEffect, useMemo, useState } from 'react'
import { purchaseOrders, sendPOReminder } from '../services/api/apiClient'
import { isValidGstin } from '../utils/validation'
import { useAuth } from '../state/authContext'
import EditPOModal from '../components/po/EditPOModal'
import CSVImportModal from '../components/po/CSVImportModal'
import ReminderModal from '../components/po/ReminderModal'
import { formatE164 } from '../utils/phone'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function PurchaseOrders() {
  const { canAccessFeature, user } = useAuth()
  const allowed = canAccessFeature('PO_MANAGEMENT')
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingId, setLoadingId] = useState(null)
  const [form, setForm] = useState({ po_number: '', vendor: '', gstin: '', vendor_email: '', vendor_phone: '', amount: '', due_date: '', status: 'open', document_url: '' })
  const [statusMessage, setStatusMessage] = useState('')
  const [cred, setCred] = useState(null)
  const [statusFilter, setStatusFilter] = useState('')
    const handleStatusFilterChange = (val) => {
      setStatusFilter(val)
      setCurrentPage(1)
    }
    const handleShowArchivedChange = (val) => {
      setShowArchived(val)
      setCurrentPage(1)
    }
    const [editingPO, setEditingPO] = useState(null)
    const [reminderPO, setReminderPO] = useState(null)
    const [showArchived, setShowArchived] = useState(false)
    const [deleteConfirm, setDeleteConfirm] = useState(null)
    const [showCSVImport, setShowCSVImport] = useState(false)
    const [currentPage, setCurrentPage] = useState(1)
    const rowsPerPage = 5

  const activeRows = useMemo(() => rows.filter(r => !r.is_archived), [rows])
  const archivedRows = useMemo(() => rows.filter(r => r.is_archived), [rows])
  const filteredRows = useMemo(() => {
    if (!statusFilter) return activeRows
    const sf = statusFilter.toLowerCase()
    return activeRows.filter(r => (String(r.status || '').toLowerCase().includes(sf)))
  }, [activeRows, statusFilter])
  const displayRows = showArchived ? rows : filteredRows
  const paginatedRows = useMemo(() => {
    return displayRows.slice(
      (currentPage - 1) * rowsPerPage,
      currentPage * rowsPerPage
    )
  }, [displayRows, currentPage, rowsPerPage])

  const getStatusBadge = (row) => {
    const statusLower = String(row.status || '').toLowerCase()
    const isPaid = row.payment_completed_at || statusLower === 'closed' || statusLower === 'paid'
    const isPending = statusLower.includes('pending')
    
    // Check overdue
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const dueDate = row.due_date ? new Date(row.due_date) : null
    const isOverdue = !isPaid && dueDate && dueDate < today

    if (isPaid) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-500"></span>
          Paid
        </span>
      )
    }
    if (isOverdue) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-red-500"></span>
          Overdue
        </span>
      )
    }
    if (isPending) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-amber-500"></span>
          Pending
        </span>
      )
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
        <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-blue-500"></span>
        Open
      </span>
    )
  }

  const totalPages = Math.ceil(displayRows.length / rowsPerPage)
  const total = useMemo(() => activeRows.reduce((sum, r) => sum + Number(r.amount || 0), 0), [activeRows])
  const stats = useMemo(() => {
    const completed = activeRows.filter(r => r.payment_completed_at || String(r.status || '').toLowerCase() === 'closed').length
    const pending = activeRows.filter(r => String(r.status || '').toLowerCase().includes('pending')).length
    const totalCount = activeRows.length
    return { totalCount, completed, pending }
  }, [activeRows])

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const res = await purchaseOrders.list(1, 100, true)
      if (res.ok && Array.isArray(res.data?.items)) {
        setRows(res.data.items)
      } else if (res.ok && Array.isArray(res.data)) {
        setRows(res.data)
      }
      setLoading(false)
    }
    fetchData()
    // Load credibility index for current user's company
    async function fetchCred() {
      try {
        const cid = user?.company_id
        if (!cid) return
        const resp = await fetch(`/api/v1/credibility/${cid}`, { credentials: 'include' })
        if (resp.ok) {
          const j = await resp.json()
          if (j?.success && j.data) setCred(j.data)
        }
      } catch (err) { String(err) }
    }
    fetchCred()
    const onChanged = () => {
      fetchCred()
    }
    window.addEventListener('poChanged', onChanged)
    return () => window.removeEventListener('poChanged', onChanged)
  }, [user?.company_id])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatusMessage('')
    if (!allowed) {
      setStatusMessage('Upgrade plan to add purchase orders.')
      return
    }
    if (!form.po_number || !form.vendor || !form.amount || !form.due_date || !form.gstin) {
      setStatusMessage('Fill all required fields.')
      return
    }

    if (form.vendor_email && (!form.vendor_email.includes('@') || !form.vendor_email.includes('.'))) {
      setStatusMessage('Enter a valid vendor email address')
      return
    }
    if (form.vendor_phone) {
      const e164 = formatE164(form.vendor_phone)
      if (!e164) {
        setStatusMessage('Enter a valid vendor phone number (e.g., +91XXXXXXXXXX)')
        return
      }
    }

    const payload = {
      po_number: form.po_number.trim(),
      vendor: form.vendor.trim(),
      gstin: form.gstin.trim().toUpperCase(),
      vendor_email: form.vendor_email?.trim() || '',
      vendor_phone: form.vendor_phone ? formatE164(form.vendor_phone) : '',
      amount: Number(form.amount),
      due_date: form.due_date,
      status: form.status,
      document_url: form.document_url || '',
    }

    setIsLoading(true)
    try {
      const res = await purchaseOrders.create(payload)
      if (!res.ok) {
        setStatusMessage(res.error || 'Failed to save PO')
        return
      }
    } catch (err) {
      setStatusMessage(err?.message || 'Failed to save PO')
      return
    } finally {
      setIsLoading(false)
    }

    // Refresh list from backend to ensure consistency
    setLoading(true)
    const resList = await purchaseOrders.list(1, 100, true)
    if (resList.ok && Array.isArray(resList.data?.items)) {
      setRows(resList.data.items)
    } else if (resList.ok && Array.isArray(resList.data)) {
      setRows(resList.data)
    }
    setLoading(false)
    setForm({ po_number: '', vendor: '', gstin: '', vendor_email: '', vendor_phone: '', amount: '', due_date: '', status: 'open', document_url: '' })
    setStatusMessage('PO saved to backend successfully.')
    window.dispatchEvent(new Event('poChanged'))
  }

    const handleEdit = (po) => {
      setEditingPO(po)
    }

    const handleSaveEdit = async (payload) => {
      const res = await purchaseOrders.update(editingPO.id, payload)
      if (res.ok) {
        // Refresh list after edit
        const resList = await purchaseOrders.list(1, 100, true)
        if (resList.ok && Array.isArray(resList.data?.items)) {
          setRows(resList.data.items)
        } else if (resList.ok && Array.isArray(resList.data)) {
          setRows(resList.data)
        }
        setStatusMessage('PO updated successfully.')
        window.dispatchEvent(new Event('poChanged'))
        return true
      }
      return false
    }

    const handleDelete = (po) => {
      setDeleteConfirm(po)
    }

    const confirmDelete = async () => {
      if (!deleteConfirm) return
      const res = await purchaseOrders.delete(deleteConfirm.id)
      if (res.ok) {
        setRows((prev) => prev.filter(r => r.id !== deleteConfirm.id))
        setStatusMessage('PO deleted permanently.')
        window.dispatchEvent(new Event('poChanged'))
      } else {
        setStatusMessage(res.error || 'Failed to delete PO')
      }
      setDeleteConfirm(null)
    }

    const handleArchive = async (po) => {
      const res = await purchaseOrders.archive(po.id)
      if (res.ok) {
        setRows((prev) => prev.map(r => r.id === po.id ? { ...r, is_archived: !r.is_archived } : r))
        setStatusMessage(po.is_archived ? 'PO restored from archive.' : 'PO archived.')
        window.dispatchEvent(new Event('poChanged'))
      } else {
        setStatusMessage(res.error || 'Failed to archive PO')
      }
    }
  
    const handleSendReminder = (po) => {
      setStatusMessage('')
      const email = (po.vendor_email || '').trim()
      if (!email) {
        setStatusMessage('No vendor email set for this PO. Please edit the PO to add vendor contact details.')
        return
      }
      setReminderPO(po)
    }

    const handleConfirmReminder = async (payload) => {
      const res = await sendPOReminder(reminderPO.id, payload)
      if (res.ok) {
        if (payload.scheduled_at) {
          const dt = new Date(payload.scheduled_at).toLocaleString()
          setStatusMessage(`Reminder scheduled for ${dt}`)
        } else {
          setStatusMessage('Reminder sent to vendor')
        }
        return true
      } else {
        setStatusMessage(res.error || 'Failed to process reminder')
        return false
      }
    }
  
    const handleMarkPaid = async (po) => {
      setLoadingId(po.id)
      const res = await purchaseOrders.markPaid(po.id)
      if (res.ok) {
        setStatusMessage('PO marked as paid.')
        setLoading(true)
        const resList = await purchaseOrders.list(1, 100, true)
        if (resList.ok && Array.isArray(resList.data?.items)) {
          setRows(resList.data.items)
        } else if (resList.ok && Array.isArray(resList.data)) {
          setRows(resList.data)
        }
        setLoading(false)
        window.dispatchEvent(new Event('poChanged'))
      } else {
        setStatusMessage(res.error || 'Failed to mark as paid')
      }
      setLoadingId(null)
    }
  
    const handleImportComplete = async () => {
      // Refresh the list after import
      setLoading(true)
      const res = await purchaseOrders.list(1, 100, true)
      if (res.ok && Array.isArray(res.data?.items)) {
        setRows(res.data.items)
      } else if (res.ok && Array.isArray(res.data)) {
        setRows(res.data)
      }
      setLoading(false)
      setStatusMessage('CSV import completed.')
      window.dispatchEvent(new Event('poChanged'))
    }

    const downloadTemplate = () => {
      const headers = [
        'number','vendor_name','vendor_gstin',
        'vendor_email','vendor_phone','amount',
        'due_date','status','document_url'
      ]
      const example = [
        'PO-2026-01','Test Vendor','22AAAAA0000A1Z5',
        'vendor@email.com','+919876543210',
        '50000','2026-04-01','Open',''
      ]
      const csv = [headers.join(','), example.join(',')].join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'PO_Upload_Template.csv'
      a.click()
      URL.revokeObjectURL(url)
    }

  return (
    <section className="py-6 md:py-8">
      {isLoading && <LoadingSpinner />}
      <div className="container-custom space-y-4">
        <div className="space-y-1">
          <p className="text-sm text-gray-500">PO Management</p>
          <h1 className="text-2xl font-heading font-bold text-gray-900">Purchase Orders</h1>
          <p className="text-gray-600 max-w-3xl text-sm">Log and track purchase orders; attach documents for audit trails.</p>
        </div>

        {/* Credibility Index Highlight */}
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-heading font-semibold text-amber-900">Business Credibility Index</h2>
                {cred && (
                  <span
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${cred.grade === 'A' ? 'bg-emerald-100 text-emerald-800' : cred.grade === 'B' ? 'bg-blue-100 text-blue-800' : cred.grade === 'C' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}
                    title="Grade reflects on-time payments and delays"
                  >
                    Grade {cred.grade}
                  </span>
                )}
              </div>
              <p className="text-amber-800/90 text-sm mt-1 max-w-2xl">
                A higher score indicates more consistent on‑time payments and lower credit risk.
              </p>
            </div>
            {cred && (
              <div className="flex items-center gap-2" title="Risk level derived from score and payment behavior">
                <span className="text-sm text-amber-800">Risk</span>
                <span className={`text-lg ${cred.risk_level === 'Low' ? 'text-emerald-600' : cred.risk_level === 'Medium' ? 'text-amber-600' : 'text-red-600'}`}>
                  {cred.risk_level === 'Low' ? '✅' : cred.risk_level === 'Medium' ? '⚠️' : '❌'}
                </span>
                <span className="text-sm font-medium text-amber-900">{cred.risk_level}</span>
              </div>
            )}
          </div>
          <div className="mt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-amber-800">Score</span>
              <span className="text-sm font-semibold text-amber-900">{cred?.score ?? '—'}</span>
            </div>
            <div className="h-2 w-full rounded-full bg-amber-100 overflow-hidden">
              <div
                className={`h-full ${((cred?.score || 0) >= 70) ? 'bg-emerald-500' : ((cred?.score || 0) >= 40) ? 'bg-amber-500' : 'bg-red-500'}`}
                style={{ width: `${Math.max(0, Math.min(100, cred?.score || 0))}%` }}
              />
            </div>
          </div>
          <div className="mt-4 grid sm:grid-cols-3 gap-3" title="Fulfillment stats from your active purchase orders">
            <div className="p-3 rounded-lg bg-white/60 border border-amber-100">
              <p className="text-xs text-amber-700">Total POs</p>
              <p className="font-semibold text-amber-900">{stats.totalCount}</p>
              <div className="h-1 mt-1 bg-amber-100 rounded">
                <div className="h-full bg-amber-400 rounded" style={{ width: `${stats.totalCount ? 100 : 0}%` }} />
              </div>
            </div>
            <div className="p-3 rounded-lg bg-white/60 border border-amber-100">
              <p className="text-xs text-amber-700">Completed POs</p>
              <p className="font-semibold text-emerald-700">{stats.completed}</p>
              <div className="h-1 mt-1 bg-emerald-100 rounded" title="Ratio of completed to total">
                <div className="h-full bg-emerald-500 rounded" style={{ width: `${stats.totalCount ? Math.round((stats.completed / stats.totalCount) * 100) : 0}%` }} />
              </div>
            </div>
            <div className="p-3 rounded-lg bg-white/60 border border-amber-100">
              <p className="text-xs text-amber-700">Pending POs</p>
              <p className="font-semibold text-amber-700">{stats.pending}</p>
              <div className="h-1 mt-1 bg-amber-100 rounded" title="Ratio of pending to total">
                <div className="h-full bg-amber-500 rounded" style={{ width: `${stats.totalCount ? Math.round((stats.pending / stats.totalCount) * 100) : 0}%` }} />
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-4 items-start">
          <div className="card flex-[2] shadow-sm rounded-xl overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-heading font-semibold text-gray-900">Open POs</h2>
                {allowed && (
                  <button
                    onClick={() => setShowCSVImport(true)}
                    className="text-sm px-3 py-1 rounded-lg bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors font-medium"
                    title="Import from CSV"
                  >
                    Import CSV
                  </button>
                )}
              </div>
              <div className="flex items-center gap-4">
                <div className="hidden sm:flex items-center gap-2">
                  <button onClick={() => handleStatusFilterChange('')} className={`text-xs px-2.5 py-1 rounded-lg ${!statusFilter ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-700'}`}>All</button>
                  <button onClick={() => handleStatusFilterChange('Open')} className={`text-xs px-2.5 py-1 rounded-lg ${statusFilter === 'Open' ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-700'}`}>Open</button>
                  <button onClick={() => handleStatusFilterChange('Pending')} className={`text-xs px-2.5 py-1 rounded-lg ${statusFilter === 'Pending' ? 'bg-amber-600 text-white' : 'bg-amber-50 text-amber-700'}`}>Pending</button>
                  <button onClick={() => handleStatusFilterChange('Closed')} className={`text-xs px-2.5 py-1 rounded-lg ${statusFilter === 'Closed' ? 'bg-emerald-600 text-white' : 'bg-emerald-50 text-emerald-700'}`}>Closed</button>
                </div>
                <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showArchived}
                    onChange={(e) => handleShowArchivedChange(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  {' '}
                  Show Archived
                </label>
                <p className="text-sm text-gray-500">Total: ₹{total.toLocaleString('en-IN')}</p>
              </div>
              </div>
              {archivedRows.length > 0 && (
                <p className="text-xs text-gray-500 mb-3">{archivedRows.length} archived PO(s)</p>
              )}
            <div className="overflow-x-auto border border-gray-100 rounded-xl shadow-sm">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50/80 sticky top-0 z-10 backdrop-blur-sm">
                  <tr>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">PO #</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Vendor</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Email</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Mobile</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">GSTIN</th>
                    <th className="py-5 px-6 text-right text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Amount</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Due</th>
                    <th className="py-5 px-6 text-left text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Status</th>
                    <th className="py-5 px-6 text-right text-xs font-bold text-gray-800 uppercase tracking-widest border-b border-gray-200">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {loading && (
                    <tr>
                      <td colSpan={9} className="py-12 text-center text-gray-500">
                        <div className="flex flex-col items-center gap-2">
                          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-100 border-t-primary-600" />
                          <p className="text-sm font-medium">Loading orders...</p>
                        </div>
                      </td>
                    </tr>
                  )}
                  {!loading && displayRows.length === 0 && (
                    <tr>
                      <td colSpan={9} className="py-12 text-center text-gray-500">
                        <div className="flex flex-col items-center gap-1">
                          <span className="text-2xl">📋</span>
                          <p className="text-sm font-medium">{showArchived ? 'No purchase orders yet.' : 'No active purchase orders.'}</p>
                        </div>
                      </td>
                    </tr>
                  )}
                  {paginatedRows.map((row) => {
                    const statusLower = String(row.status || '').toLowerCase()
                    const isPending = statusLower.includes('pending')
                    const isPaid = row.payment_completed_at || statusLower === 'closed' || statusLower === 'paid'
                    return (
                      <tr 
                        key={row.id} 
                        className={`group transition-colors duration-150 even:bg-gray-50/30 hover:bg-blue-50/50 ${row.is_archived ? 'opacity-50 grayscale-[0.5]' : ''} ${isPending ? 'bg-amber-50/40' : ''}`}
                      >
                        <td className="py-5 px-6 whitespace-nowrap">
                          <span className="font-bold text-gray-900">{row.po_number}</span>
                        </td>
                        <td className="py-5 px-6">
                          <div className="text-sm font-medium text-gray-900">{row.vendor}</div>
                        </td>
                        <td className="py-5 px-6 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{(row.vendor_email || '').trim() ? row.vendor_email : '—'}</div>
                        </td>
                        <td className="py-5 px-6 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{(row.vendor_phone || '').trim() ? row.vendor_phone : '—'}</div>
                        </td>
                        <td className="py-5 px-6 whitespace-nowrap">
                          <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded border border-gray-200 text-gray-700">{row.gstin}</span>
                        </td>
                        <td className="py-5 px-6 text-right whitespace-nowrap">
                          <span className="font-semibold text-gray-900">₹{Number(row.amount).toLocaleString('en-IN')}</span>
                        </td>
                        <td className="py-5 px-6 whitespace-nowrap">
                          <span className="text-sm text-gray-600 font-medium">{row.due_date?.slice(0, 10) || row.due_date}</span>
                        </td>
                        <td className="py-5 px-6 whitespace-nowrap">
                          {getStatusBadge(row)}
                        </td>
                        <td className="py-5 px-6 text-right whitespace-nowrap">
                          <div className="flex justify-end gap-1.5">
                            {loadingId === row.id ? (
                              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-200 border-t-primary-600" />
                            ) : (
                              <>
                                <button
                                  onClick={() => handleMarkPaid(row)}
                                  className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-100 hover:text-emerald-700 transition-colors shadow-sm"
                                  title="Mark as paid"
                                >
                                  <span className="text-sm">✅</span>
                                </button>
                                <button
                                  onClick={() => handleEdit(row)}
                                  className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700 transition-colors shadow-sm"
                                  title="Edit"
                                >
                                  <span className="text-sm">✏️</span>
                                </button>
                                <button
                                  onClick={() => handleSendReminder(row)}
                                  disabled={isPaid}
                                  className={`p-1.5 rounded-lg transition-colors shadow-sm ${
                                    isPaid 
                                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-50' 
                                      : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-700'
                                  }`}
                                  title={isPaid ? 'Reminder not available for paid PO' : 'Send Reminder'}
                                >
                                  <span className="text-sm">📧</span>
                                </button>
                                <button
                                  onClick={() => handleArchive(row)}
                                  className="p-1.5 rounded-lg bg-amber-50 text-amber-600 hover:bg-amber-100 hover:text-amber-700 transition-colors shadow-sm"
                                  title={row.is_archived ? 'Restore' : 'Archive'}
                                >
                                  <span className="text-sm">🗄️</span>
                                </button>
                                <button
                                  onClick={() => handleDelete(row)}
                                  className="p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 transition-colors shadow-sm"
                                  title="Delete"
                                >
                                  <span className="text-sm">🗑️</span>
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 px-2">
                <p className="text-sm text-gray-500">
                  Page <span className="font-medium">{currentPage}</span> of <span className="font-medium">{totalPages}</span>
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}

            {!allowed && (
              <p className="text-xs text-amber-700 mt-3">Upgrade plan to manage purchase orders.</p>
            )}
          </div>

          <div className="card flex-[1] space-y-3 self-start sticky top-4 rounded-xl border border-gray-100 shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h2 className="text-base font-bold text-gray-700">Add PO</h2>
                <button 
                  onClick={downloadTemplate} 
                  className="text-xs text-blue-600 border border-blue-600 px-2 py-1 rounded hover:bg-blue-50 transition-colors" 
                > 
                  📥 Download Template 
                </button>
              </div>
              {!allowed && <span className="text-xs text-amber-700">Gated</span>}
            </div>
            {statusMessage && (
              <div className="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2 text-xs text-gray-700">
                {statusMessage}
              </div>
            )}
            <form className="space-y-3" onSubmit={handleSubmit}>
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="po_number"
                value={form.po_number || ''}
                onChange={handleChange}
                placeholder="PO Number"
                required
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="vendor"
                value={form.vendor || ''}
                onChange={handleChange}
                placeholder="Vendor Name"
                required
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="gstin"
                value={form.gstin || ''}
                onChange={handleChange}
                placeholder="Vendor GSTIN"
                required
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                type="email"
                name="vendor_email"
                value={form.vendor_email || ''}
                onChange={handleChange}
                placeholder="Vendor Email ID"
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="vendor_phone"
                value={form.vendor_phone || ''}
                onChange={handleChange}
                placeholder="Vendor Mobile Number"
              />
              <div className="flex gap-3">
                <input
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  name="amount"
                  type="number"
                  value={form.amount || ''}
                  onChange={handleChange}
                  placeholder="Amount"
                  required
                />
                <input
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  name="due_date"
                  type="date"
                  value={form.due_date || ''}
                  onChange={handleChange}
                  required
                />
              </div>
              <select
                name="status"
                value={form.status || 'Open'}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              >
                <option value="Open">Open</option>
                <option value="Pending Docs">Pending Docs</option>
                <option value="Closed">Closed</option>
              </select>
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="document_url"
                value={form.document_url || ''}
                onChange={handleChange}
                placeholder="Document URL (optional)"
              />
              <button type="submit" className="btn-primary w-full" disabled={!allowed}>
                {allowed ? 'Save PO' : 'Upgrade to enable'}
              </button>
            </form>
          </div>
        </div>

          {editingPO && (
            <EditPOModal
              po={editingPO}
              onClose={() => setEditingPO(null)}
              onSave={handleSaveEdit}
            />
          )}

          {reminderPO && (
            <ReminderModal
              po={reminderPO}
              onClose={() => setReminderPO(null)}
              onSend={handleConfirmReminder}
            />
          )}

          {showCSVImport && (
            <CSVImportModal
              onClose={() => setShowCSVImport(false)}
              onImportComplete={handleImportComplete}
            />
          )}

          {deleteConfirm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-2">Confirm Delete</h3>
                <p className="text-gray-600 mb-4">
                  Are you sure you want to permanently delete PO <strong>{deleteConfirm.po_number}</strong>?
                  This action cannot be undone.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setDeleteConfirm(null)}
                    className="flex-1 px-6 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmDelete}
                    className="flex-1 px-6 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          )}
      </div>
    </section>
  )
}
