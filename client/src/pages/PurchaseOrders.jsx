import { useEffect, useMemo, useState } from 'react'
import { purchaseOrders } from '../services/api/apiClient'
import { isValidGstin } from '../utils/validation'
import { useAuth } from '../state/authContext'
import EditPOModal from '../components/po/EditPOModal'
import CSVImportModal from '../components/po/CSVImportModal'

export default function PurchaseOrders() {
  const { canAccessFeature } = useAuth()
  const allowed = canAccessFeature('PO_MANAGEMENT')
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ number: '', vendor_name: '', vendor_gstin: '', amount: '', due_date: '', status: 'open', document_url: '' })
  const [statusMessage, setStatusMessage] = useState('')
    const [editingPO, setEditingPO] = useState(null)
    const [showArchived, setShowArchived] = useState(false)
    const [deleteConfirm, setDeleteConfirm] = useState(null)
    const [showCSVImport, setShowCSVImport] = useState(false)

    const activeRows = useMemo(() => rows.filter(r => !r.is_archived), [rows])
    const archivedRows = useMemo(() => rows.filter(r => r.is_archived), [rows])
    const displayRows = showArchived ? rows : activeRows
    const total = useMemo(() => activeRows.reduce((sum, r) => sum + Number(r.amount || 0), 0), [activeRows])

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
  }, [])

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
    if (!isValidGstin(form.vendor_gstin)) {
      setStatusMessage('Enter a valid vendor GSTIN to proceed.')
      return
    }
    if (!form.number || !form.vendor_name || !form.amount || !form.due_date) {
      setStatusMessage('Fill all required fields.')
      return
    }

    const payload = {
      number: form.number.trim(),
      vendor_name: form.vendor_name.trim(),
      vendor_gstin: form.vendor_gstin.trim().toUpperCase(),
      amount: Number(form.amount),
      due_date: form.due_date,
      status: form.status,
      document_url: form.document_url || '',
    }

    const res = await purchaseOrders.create(payload)
    if (!res.ok) {
      setStatusMessage(res.error || 'Failed to create purchase order')
      return
    }

    setRows((prev) => [res.data, ...prev])
    setForm({ number: '', vendor_name: '', vendor_gstin: '', amount: '', due_date: '', status: 'open', document_url: '' })
    setStatusMessage('PO saved to backend successfully.')
    window.dispatchEvent(new Event('poChanged'))
  }

    const handleEdit = (po) => {
      setEditingPO(po)
    }

    const handleSaveEdit = async (payload) => {
      const res = await purchaseOrders.update(editingPO.id, payload)
      if (res.ok) {
        setRows((prev) => prev.map(r => r.id === editingPO.id ? { ...r, ...payload } : r))
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
  return (
    <section className="section-padding">
      <div className="container-custom space-y-8">
        <div className="space-y-2">
          <p className="text-sm text-gray-500">PO Management</p>
          <h1 className="text-3xl font-heading font-bold text-gray-900">Purchase Orders</h1>
          <p className="text-gray-600 max-w-3xl">Log and track purchase orders; attach documents for audit trails. This is client-only with local state.</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="card lg:col-span-2">
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
                  <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showArchived}
                      onChange={(e) => setShowArchived(e.target.checked)}
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
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-600">
                    <th className="py-2 pr-3">PO #</th>
                    <th className="py-2 pr-3">Vendor</th>
                    <th className="py-2 pr-3">GSTIN</th>
                    <th className="py-2 pr-3">Amount</th>
                    <th className="py-2 pr-3">Due</th>
                    <th className="py-2 pr-3">Status</th>
                      <th className="py-2">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {loading && (
                    <tr>
                        <td colSpan={7} className="py-3 text-center text-gray-500">Loading...</td>
                    </tr>
                  )}
                    {!loading && displayRows.length === 0 && (
                    <tr>
                        <td colSpan={7} className="py-3 text-center text-gray-500">
                          {showArchived ? 'No purchase orders yet.' : 'No active purchase orders.'}
                        </td>
                    </tr>
                  )}
                    {displayRows.map((row) => (
                      <tr key={row.id} className={`text-gray-800 ${row.is_archived ? 'opacity-50' : ''}`}>
                      <td className="py-2 pr-3 font-semibold">{row.number}</td>
                      <td className="py-2 pr-3">{row.vendor_name}</td>
                      <td className="py-2 pr-3">{row.vendor_gstin}</td>
                      <td className="py-2 pr-3">₹{Number(row.amount).toLocaleString('en-IN')}</td>
                      <td className="py-2 pr-3">{row.due_date?.slice(0, 10) || row.due_date}</td>
                        <td className="py-2 pr-3">
                          <span className="capitalize">{row.status}</span>
                          {row.is_archived && <span className="ml-2 text-xs text-gray-500">(Archived)</span>}
                        </td>
                        <td className="py-2">
                          <div className="flex gap-2">
                            {!row.is_archived && (
                              <button
                                onClick={() => handleEdit(row)}
                                className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                                title="Edit"
                              >
                                Edit
                              </button>
                            )}
                            <button
                              onClick={() => handleArchive(row)}
                              className="text-amber-600 hover:text-amber-800 text-xs font-medium"
                              title={row.is_archived ? 'Restore' : 'Archive'}
                            >
                              {row.is_archived ? 'Restore' : 'Archive'}
                            </button>
                            <button
                              onClick={() => handleDelete(row)}
                              className="text-red-600 hover:text-red-800 text-xs font-medium"
                              title="Delete"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!allowed && (
              <p className="text-xs text-amber-700 mt-3">Upgrade plan to manage purchase orders.</p>
            )}
          </div>

          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-heading font-semibold text-gray-900">Add PO</h2>
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
                name="number"
                value={form.number}
                onChange={handleChange}
                placeholder="PO Number"
                required
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="vendor_name"
                value={form.vendor_name}
                onChange={handleChange}
                placeholder="Vendor Name"
                required
              />
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="vendor_gstin"
                value={form.vendor_gstin}
                onChange={handleChange}
                placeholder="Vendor GSTIN"
                required
              />
              <div className="flex gap-3">
                <input
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  name="amount"
                  type="number"
                  value={form.amount}
                  onChange={handleChange}
                  placeholder="Amount"
                  required
                />
                <input
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  name="due_date"
                  type="date"
                  value={form.due_date}
                  onChange={handleChange}
                  required
                />
              </div>
              <select
                name="status"
                value={form.status}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              >
                <option value="open">Open</option>
                <option value="pending">Pending Docs</option>
                <option value="closed">Closed</option>
              </select>
              <input
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="document_url"
                value={form.document_url}
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
                  Are you sure you want to permanently delete PO <strong>{deleteConfirm.number}</strong>?
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
