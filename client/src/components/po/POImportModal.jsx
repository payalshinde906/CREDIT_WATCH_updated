
import { useState } from 'react'
import PropTypes from 'prop-types'
import { purchaseOrders } from '../../services/api/apiClient'

export default function POImportModal({ onClose, onImportComplete }) {
  const [file, setFile] = useState(null)
  const [source, setSource] = useState('default')
  const [importing, setImporting] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      const isAllowed = selectedFile.name.endsWith('.csv') || 
                        selectedFile.name.endsWith('.xlsx') || 
                        selectedFile.name.endsWith('.xls')
      
      if (!isAllowed) {
        setError('Please select a CSV or Excel file (.csv, .xlsx, .xls)')
        return
      }
      setFile(selectedFile)
      setError('')
    }
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
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source', source)

      const res = await purchaseOrders.bulkImport(formData)
      
      if (res.ok) {
        setResults(res.data)
        if (res.data.success > 0) {
          onImportComplete()
        }
      } else {
        throw new Error(res.error || 'Failed to import purchase orders')
      }
    } catch (err) {
      console.error('[PO Import]', err)
      setError(err.message || 'Failed to process file')
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-heading font-bold text-gray-900">Import Purchase Orders</h2>
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

        <div className="p-6 space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Smart Import Features</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Supports CSV and Excel (.xlsx, .xls) formats</li>
              <li>• Automatically detects header rows and removes extra top rows</li>
              <li>• Auto-maps columns for Zoho and Tally exports</li>
              <li>• Calculates "Days Left" and derives "Status" automatically</li>
            </ul>
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {results && (
            <div className={`rounded-lg border px-4 py-3 ${results.failed > 0 ? 'bg-orange-50 border-orange-200' : 'bg-green-50 border-green-200'}`}>
              <h3 className={`font-semibold mb-2 ${results.failed > 0 ? 'text-orange-900' : 'text-green-900'}`}>Import Results</h3>
              <div className={`text-sm space-y-1 ${results.failed > 0 ? 'text-orange-800' : 'text-green-800'}`}>
                <p>Total processed: {results.total}</p>
                <p>Successfully imported: {results.success}</p>
                <p>Failed: {results.failed}</p>
              </div>
              {results.errors?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-red-700">Top errors:</p>
                  <ul className="text-xs text-red-600 space-y-1 mt-1">
                    {results.errors.map((err, i) => (
                      <li key={i}>• {err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {!results && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Import Source
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {['Default', 'Zoho', 'Tally'].map((opt) => (
                    <button
                      key={opt}
                      onClick={() => setSource(opt.toLowerCase())}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                        source === opt.toLowerCase()
                          ? 'bg-primary-50 border-primary-600 text-primary-700'
                          : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                      type="button"
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Selecting Zoho or Tally will automatically map their specific column names to our system.
                </p>
              </div>

              <div>
                <label htmlFor="import-file" className="block text-sm font-medium text-gray-700 mb-2">
                  Select File (CSV or Excel)
                </label>
                <div className="relative group">
                  <input
                    id="import-file"
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    disabled={importing}
                  />
                  <div className={`w-full py-8 px-4 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-colors ${
                    file ? 'border-primary-300 bg-primary-50' : 'border-gray-300 group-hover:border-primary-400'
                  }`}>
                    <svg className={`w-10 h-10 mb-2 ${file ? 'text-primary-500' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span className="text-sm font-medium text-gray-600">
                      {file ? file.name : 'Click or drag file to upload'}
                    </span>
                    <span className="text-xs text-gray-400 mt-1">
                      Max file size: 10MB
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}

          <div className="flex gap-3 pt-4">
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors font-medium"
              disabled={importing}
            >
              {results ? 'Done' : 'Cancel'}
            </button>
            {!results && (
              <button
                onClick={handleImport}
                className="flex-1 btn-primary disabled:opacity-50"
                disabled={!file || importing}
              >
                {importing ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Processing...
                  </span>
                ) : 'Process & Import'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

POImportModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  onImportComplete: PropTypes.func.isRequired,
}
