import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { isValidGstin } from '../../utils/validation'

export default function EditPOModal({ po, onClose, onSave }) {
  const [form, setForm] = useState({
    number: '',
    vendor_name: '',
    vendor_gstin: '',
    amount: '',
    due_date: '',
    status: 'open',
    notes: '',
    document_url: '',
    reason: '',
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (po) {
      setForm({
        number: po.number || '',
        vendor_name: po.vendor_name || '',
        vendor_gstin: po.vendor_gstin || '',
        amount: po.amount || '',
        due_date: po.due_date?.slice(0, 10) || '',
        status: po.status || 'open',
        notes: po.notes || '',
        document_url: po.document_url || '',
      })
    }
  }, [po])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!isValidGstin(form.vendor_gstin)) {
      setError('Enter a valid vendor GSTIN to proceed.')
      return
    }

    if (!form.number || !form.vendor_name || !form.amount || !form.due_date || !form.reason) {
      setError('Fill all required fields (including reason).')
      return
    }

    const payload = {
      number: form.number.trim(),
      vendor_name: form.vendor_name.trim(),
      vendor_gstin: form.vendor_gstin.trim().toUpperCase(),
      amount: Number(form.amount),
      due_date: form.due_date,
      status: form.status,
      notes: form.notes?.trim() || '',
      document_url: form.document_url?.trim() || '',
      reason: form.reason.trim(),
    }

    setSaving(true)
    const success = await onSave(payload)
    setSaving(false)

    if (success) {
      onClose()
    } else {
      setError('Failed to update purchase order')
    }
  }

  if (!po) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-heading font-bold text-gray-900">Edit Purchase Order</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              type="button"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="po-number" className="block text-sm font-medium text-gray-700 mb-1">
                PO Number <span className="text-red-500">*</span>
              </label>
              <input
                id="po-number"
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="number"
                value={form.number}
                onChange={handleChange}
                placeholder="PO-2024-001"
                required
              />
            </div>

            <div>
              <label htmlFor="po-status" className="block text-sm font-medium text-gray-700 mb-1">
                Status <span className="text-red-500">*</span>
              </label>
              <select
                id="po-status"
                name="status"
                value={form.status}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                required
              >
                <option value="open">Open</option>
                <option value="pending">Pending Docs</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="vendor-name2" className="block text-sm font-medium text-gray-700 mb-1">
              Vendor Name <span className="text-red-500">*</span>
            </label>
            <input
              id="vendor-name2"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              name="vendor_name"
              value={form.vendor_name}
              onChange={handleChange}
              placeholder="ABC Suppliers Pvt Ltd"
              required
            />
          </div>

          <div>
            <label htmlFor="vendor-gstin" className="block text-sm font-medium text-gray-700 mb-1">
              Vendor GSTIN <span className="text-red-500">*</span>
            </label>
            <input
              id="vendor-gstin"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              name="vendor_gstin"
              value={form.vendor_gstin}
              onChange={handleChange}
              placeholder="27AABCU9603R1ZM"
              required
            />
          </div>

          <div>
            <label htmlFor="vendor-email" className="block text-sm font-medium text-gray-700 mb-1">
              Vendor Email
            </label>
            <input
              id="vendor-email"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              name="vendor_email"
              type="email"
              value={form.vendor_email}
              onChange={handleChange}
              placeholder="vendor@example.com"
            />
          </div>

          <div>
            <label htmlFor="vendor-phone" className="block text-sm font-medium text-gray-700 mb-1">
              Vendor Phone
            </label>
            <input
              id="vendor-phone"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              name="vendor_phone"
              value={form.vendor_phone}
              onChange={handleChange}
              placeholder="+91..."
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="po-amount" className="block text-sm font-medium text-gray-700 mb-1">
                Amount (₹) <span className="text-red-500">*</span>
              </label>
              <input
                id="po-amount"
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="amount"
                type="number"
                step="0.01"
                value={form.amount}
                onChange={handleChange}
                placeholder="50000"
                required
              />
            </div>

            <div>
              <label htmlFor="due-date" className="block text-sm font-medium text-gray-700 mb-1">
                Due Date <span className="text-red-500">*</span>
              </label>
              <input
                id="due-date"
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                name="due_date"
                type="date"
                value={form.due_date}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="po-notes" className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              id="po-notes"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 min-h-[80px]"
              name="notes"
              value={form.notes}
              onChange={handleChange}
              placeholder="Additional notes or comments..."
            />
          </div>

          <div>
            <label htmlFor="document-url" className="block text-sm font-medium text-gray-700 mb-1">
              Document URL
            </label>
            <input
              id="document-url"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
              name="document_url"
              value={form.document_url}
              onChange={handleChange}
              placeholder="https://drive.google.com/..."
            />
          </div>

          <div>
            <label htmlFor="po-reason" className="block text-sm font-medium text-gray-700 mb-1">
              Reason for Update <span className="text-red-500">*</span>
            </label>
            <textarea
              id="po-reason"
              className="w-full rounded-lg border border-red-300 px-4 py-3 focus:border-red-500 focus:ring-2 focus:ring-red-200 min-h-[80px]"
              name="reason"
              value={form.reason}
              onChange={handleChange}
              placeholder="Explain why you are modifying this purchase order..."
              required
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors font-medium"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 btn-primary"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

EditPOModal.propTypes = {
  po: PropTypes.shape({
    id: PropTypes.string,
    number: PropTypes.string,
    vendor_name: PropTypes.string,
    vendor_gstin: PropTypes.string,
    amount: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    due_date: PropTypes.string,
    status: PropTypes.string,
    notes: PropTypes.string,
    document_url: PropTypes.string,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
}
