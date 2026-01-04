import { useState, useEffect, useCallback } from 'react'
import { invoices as invoicesApi } from '../services/api/apiClient'

export default function Invoices() {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState(null)
  const [filterStatus, setFilterStatus] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [followUpNote, setFollowUpNote] = useState('')
  const [pagination, setPagination] = useState({ skip: 0, limit: 20, total: 0 })

  const [formData, setFormData] = useState({
    counterparty_name: '',
    counterparty_gstin: '',
    counterparty_pan: '',
    invoice_number: '',
    amount: '',
    due_date: '',
    reminder_frequency_days: 7,
    notes: '',
  })

  const fetchInvoices = useCallback(async () => {
    setLoading(true)
    const params = {
      skip: pagination.skip,
      limit: pagination.limit,
    }
    if (filterStatus) params.status = filterStatus
    if (searchQuery) params.search = searchQuery

    const response = await invoicesApi.list(params)
    if (response.ok) {
      setInvoices(response.data.invoices || [])
      setPagination((prev) => ({ ...prev, total: response.data.total || 0 }))
    } else {
      setError(response.error)
    }
    setLoading(false)
  }, [pagination.skip, pagination.limit, filterStatus, searchQuery])

  useEffect(() => {
    fetchInvoices()
  }, [fetchInvoices])

  const handleCreate = async (e) => {
    e.preventDefault()
    setError(null)

    // Validate at least one identifier
    if (!formData.counterparty_gstin && !formData.counterparty_pan) {
      setError('Either GSTIN or PAN must be provided')
      return
    }

    const response = await invoicesApi.create({
      ...formData,
      amount: Number.parseFloat(formData.amount),
      reminder_frequency_days: Number.parseInt(formData.reminder_frequency_days),
    })

    if (response.ok) {
      setShowCreateModal(false)
      resetForm()
      fetchInvoices()
    } else {
      setError(response.error)
    }
  }

  // Removed unused handleUpdate function - using API calls directly

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this invoice?')) return

    const response = await invoicesApi.delete(id)
    if (response.ok) {
      fetchInvoices()
      setShowDetailModal(false)
      setSelectedInvoice(null)
    } else {
      setError(response.error)
    }
  }

  const handleToggleAcknowledgment = async (id) => {
    const response = await invoicesApi.toggleAcknowledgment(id)
    if (response.ok) {
      fetchInvoices()
      if (selectedInvoice?.id === id) {
        setSelectedInvoice(response.data)
      }
    } else {
      setError(response.error)
    }
  }

  const handleAddFollowUpNote = async (e) => {
    e.preventDefault()
    if (!followUpNote.trim()) return

    const response = await invoicesApi.addFollowUpNote(selectedInvoice.id, followUpNote)
    if (response.ok) {
      setSelectedInvoice(response.data)
      setFollowUpNote('')
      fetchInvoices()
    } else {
      setError(response.error)
    }
  }

  const resetForm = () => {
    setFormData({
      counterparty_name: '',
      counterparty_gstin: '',
      counterparty_pan: '',
      invoice_number: '',
      amount: '',
      due_date: '',
      reminder_frequency_days: 7,
      notes: '',
    })
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'acknowledged':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'overdue':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Invoice Management</h1>
          <p className="text-gray-600">Track and manage invoices with automated reminders</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            <span className="block sm:inline">{error}</span>
            <button
              onClick={() => setError(null)}
              className="absolute top-0 bottom-0 right-0 px-4 py-3"
            >
              <span className="text-2xl">&times;</span>
            </button>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4 justify-between">
            <div className="flex gap-4 flex-1">
              <input
                type="text"
                placeholder="Search invoices..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="acknowledged">Acknowledged</option>
                <option value="overdue">Overdue</option>
              </select>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Add Invoice
            </button>
          </div>
        </div>

        {/* Invoices Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading && (
            <div className="p-8 text-center text-gray-500">Loading invoices...</div>
          )}
          {!loading && invoices.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No invoices found. Create your first invoice to get started.
            </div>
          )}
          {!loading && invoices.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Invoice #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Counterparty
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Next Reminder
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {invoice.invoice_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {invoice.counterparty_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {invoice.counterparty_gstin || invoice.counterparty_pan}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(invoice.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(invoice.due_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                            invoice.status
                          )}`}
                        >
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(invoice.reminder_next_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => {
                            setSelectedInvoice(invoice)
                            setShowDetailModal(true)
                          }}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          View
                        </button>
                        <button
                          onClick={() => handleToggleAcknowledgment(invoice.id)}
                          className="text-green-600 hover:text-green-900"
                        >
                          {invoice.status === 'acknowledged' ? 'Unack' : 'Ack'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {pagination.total > pagination.limit && (
            <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {pagination.skip + 1} to{' '}
                  {Math.min(pagination.skip + pagination.limit, pagination.total)} of{' '}
                  {pagination.total} results
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      setPagination((prev) => ({
                        ...prev,
                        skip: Math.max(0, prev.skip - prev.limit),
                      }))
                    }
                    disabled={pagination.skip === 0}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() =>
                      setPagination((prev) => ({
                        ...prev,
                        skip: prev.skip + prev.limit,
                      }))
                    }
                    disabled={pagination.skip + pagination.limit >= pagination.total}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New Invoice</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="counterparty-name" className="block text-sm font-medium text-gray-700 mb-1">
                      Counterparty Name *
                    </label>
                    <input
                      id="counterparty-name"
                      type="text"
                      required
                      value={formData.counterparty_name}
                      onChange={(e) =>
                        setFormData({ ...formData, counterparty_name: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="invoice-number" className="block text-sm font-medium text-gray-700 mb-1">
                      Invoice Number *
                    </label>
                    <input
                      id="invoice-number"
                      type="text"
                      required
                      value={formData.invoice_number}
                      onChange={(e) =>
                        setFormData({ ...formData, invoice_number: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="gstin" className="block text-sm font-medium text-gray-700 mb-1">
                      Counterparty GSTIN
                    </label>
                    <input
                      id="gstin"
                      type="text"
                      maxLength={15}
                      value={formData.counterparty_gstin}
                      onChange={(e) =>
                        setFormData({ ...formData, counterparty_gstin: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="pan" className="block text-sm font-medium text-gray-700 mb-1">
                      Counterparty PAN
                    </label>
                    <input
                      id="pan"
                      type="text"
                      maxLength={10}
                      value={formData.counterparty_pan}
                      onChange={(e) =>
                        setFormData({ ...formData, counterparty_pan: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-1">
                      Amount *
                    </label>
                    <input
                      id="amount"
                      type="number"
                      required
                      step="0.01"
                      min="0"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="due-date" className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date *
                    </label>
                    <input
                      id="due-date"
                      type="date"
                      required
                      value={formData.due_date}
                      onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label htmlFor="reminder-frequency" className="block text-sm font-medium text-gray-700 mb-1">
                      Reminder Frequency (days)
                    </label>
                    <input
                      id="reminder-frequency"
                      type="number"
                      min="1"
                      max="365"
                      value={formData.reminder_frequency_days}
                      onChange={(e) =>
                        setFormData({ ...formData, reminder_frequency_days: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    id="notes"
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false)
                      resetForm()
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Create Invoice
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Invoice {selectedInvoice.invoice_number}
                  </h2>
                  <p className="text-gray-600 mt-1">{selectedInvoice.counterparty_name}</p>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>

              {/* Invoice Details */}
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">Amount</p>
                  <p className="text-lg font-semibold">{formatCurrency(selectedInvoice.amount)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Due Date</p>
                  <p className="text-lg font-semibold">{formatDate(selectedInvoice.due_date)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <span
                    className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(
                      selectedInvoice.status
                    )}`}
                  >
                    {selectedInvoice.status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Next Reminder</p>
                  <p className="text-lg font-semibold">
                    {formatDate(selectedInvoice.reminder_next_at)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">GSTIN</p>
                  <p className="text-lg font-semibold">
                    {selectedInvoice.counterparty_gstin || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">PAN</p>
                  <p className="text-lg font-semibold">
                    {selectedInvoice.counterparty_pan || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Notes */}
              {selectedInvoice.notes && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Notes</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedInvoice.notes}</p>
                </div>
              )}

              {/* Follow-up History */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Follow-up History</h3>
                {selectedInvoice.follow_up_history?.length > 0 ? (
                  <div className="space-y-3">
                    {selectedInvoice.follow_up_history.map((entry) => (
                      <div key={`${entry.timestamp}-${entry.note}`} className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">
                          {new Date(entry.timestamp).toLocaleString('en-IN')}
                        </p>
                        <p className="text-gray-900">{entry.note}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No follow-up notes yet</p>
                )}
              </div>

              {/* Add Follow-up Note */}
              <form onSubmit={handleAddFollowUpNote} className="mb-6">
                <label htmlFor="follow-up-note" className="block text-sm font-medium text-gray-700 mb-2">
                  Add Follow-up Note
                </label>
                <textarea
                  id="follow-up-note"
                  rows={3}
                  value={followUpNote}
                  onChange={(e) => setFollowUpNote(e.target.value)}
                  placeholder="Enter follow-up note..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-2"
                />
                <button
                  type="submit"
                  disabled={!followUpNote.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Add Note
                </button>
              </form>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleToggleAcknowledgment(selectedInvoice.id)}
                  className={`px-4 py-2 rounded-md ${
                    selectedInvoice.status === 'acknowledged'
                      ? 'bg-yellow-600 hover:bg-yellow-700'
                      : 'bg-green-600 hover:bg-green-700'
                  } text-white`}
                >
                  {selectedInvoice.status === 'acknowledged' ? 'Mark Pending' : 'Acknowledge'}
                </button>
                <button
                  onClick={() => handleDelete(selectedInvoice.id)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Delete
                </button>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="ml-auto px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
