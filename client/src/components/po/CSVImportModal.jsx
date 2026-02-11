import { useState } from 'react'
import PropTypes from 'prop-types'
import { purchaseOrders } from '../../services/api/apiClient'
import { isValidGstin } from '../../utils/validation'

export default function CSVImportModal({ onClose, onImportComplete }) {
  const [file, setFile] = useState(null)
  const [importing, setImporting] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file')
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const parseCSV = (text) => {
    const lines = text.split('\n').filter(line => line.trim())
    if (lines.length < 2) {
      throw new Error('CSV file must have a header row and at least one data row')
    }

    const normalize = (h) => h.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_')
    const headers = lines[0].split(',').map(normalize)
    const requiredHeaders = ['number', 'vendor_name', 'vendor_gstin', 'amount', 'due_date']
    
    for (const required of requiredHeaders) {
      if (!headers.includes(required)) {
        throw new Error(`Missing required column: ${required}`)
      }
    }

    const rows = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      const row = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ''
      })

      // Validate required fields
      if (!row.number || !row.vendor_name || !row.vendor_gstin || !row.amount || !row.due_date) {
        throw new Error(`Row ${i}: Missing required field`)
      }

      // Validate GSTIN
      if (!isValidGstin(row.vendor_gstin)) {
        throw new Error(`Row ${i}: Invalid GSTIN format`)
      }

      // Validate amount
      const amount = Number(row.amount)
      if (Number.isNaN(amount) || amount <= 0) {
        throw new Error(`Row ${i}: Invalid amount`)
      }

      const payload = {
        number: row.number,
        vendor_name: row.vendor_name,
        vendor_gstin: row.vendor_gstin.toUpperCase(),
        amount: amount,
        due_date: row.due_date,
        status: row.status || 'open',
        notes: row.notes || '',
        document_url: row.document_url || '',
      }
      const extras = {
        order_currency: row.order_currency || row.purchase_currency || 'INR',
        supplier_address: row.supplier_address || '',
        item_summary: row.item_summary || '',
        delivery_address: row.delivery_address || '',
        invoice_address: row.invoice_address || '',
        order_date: row.order_date || '',
      }
      Object.assign(payload, extras)
      rows.push(payload)
    }

    return rows
  }

  const handleImport = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setImporting(true)
    setError('')
    setResults(null)

    try {
      const text = await file.text()
      const rows = parseCSV(text)

      const imported = []
      const failed = []

      for (const row of rows) {
        const res = await purchaseOrders.create(row)
        if (res.ok) {
          imported.push(row.number)
        } else {
          failed.push({ number: row.number, error: res.error || 'Unknown error' })
        }
      }

      setResults({
        total: rows.length,
        imported: imported.length,
        failed: failed.length,
        failedDetails: failed,
      })

      if (imported.length > 0) {
        onImportComplete()
      }
    } catch (err) {
      setError(err.message || 'Failed to parse CSV file')
    } finally {
      setImporting(false)
    }
  }

  const downloadSample = () => {
    const sample = `number,vendor_name,vendor_gstin,amount,due_date,status,notes,document_url
PO-2024-001,ABC Suppliers Ltd,27AABCU9603R1ZM,50000,2024-12-31,open,Sample PO,
PO-2024-002,XYZ Traders Pvt Ltd,29AABCT1234F1Z5,75000,2025-01-15,pending,Another sample,https://example.com/doc`
    const blob = new Blob([sample], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'po_import_sample.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-heading font-bold text-gray-900">Import POs from CSV</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              type="button"
              disabled={importing}
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">CSV Format Requirements</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Required columns: number, vendor_name, vendor_gstin, amount, due_date</li>
              <li>• Optional columns: status, notes, document_url</li>
              <li>• First row must be headers</li>
              <li>• Date format: YYYY-MM-DD</li>
              <li>• GSTIN must be valid 15-character format</li>
            </ul>
            <button
              onClick={downloadSample}
              className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium underline"
            >
              Download Sample CSV
            </button>
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {results && (
            <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3">
              <h3 className="font-semibold text-green-900 mb-2">Import Results</h3>
              <div className="text-sm text-green-800 space-y-1">
                <p>Total rows: {results.total}</p>
                <p>Successfully imported: {results.imported}</p>
                <p>Failed: {results.failed}</p>
              </div>
              {results.failedDetails.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-semibold text-red-700">Failed POs:</p>
                  <ul className="text-xs text-red-600 space-y-1 mt-1">
                    {results.failedDetails.map((f) => (
                      <li key={f.number}>{f.number}: {f.error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div>
            <label htmlFor="csv-file" className="block text-sm font-medium text-gray-700 mb-2">
              Select CSV File
            </label>
            <input
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              disabled={importing}
            />
            {file && (
              <p className="text-xs text-gray-500 mt-1">Selected: {file.name}</p>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors font-medium"
              disabled={importing}
            >
              {results ? 'Close' : 'Cancel'}
            </button>
            {!results && (
              <button
                onClick={handleImport}
                className="flex-1 btn-primary"
                disabled={!file || importing}
              >
                {importing ? 'Importing...' : 'Import POs'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

CSVImportModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  onImportComplete: PropTypes.func.isRequired,
}
