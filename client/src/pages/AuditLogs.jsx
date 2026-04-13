import { useState, useEffect } from 'react' 
import { useAuth } from '../state/authContext' 
import { audit } from '../services/api/apiClient'

const ACTION_COLORS = { 
  CREATE: { bg: 'bg-green-100', text: 'text-green-700', label: '✅ CREATE' }, 
  UPDATE: { bg: 'bg-blue-100', text: 'text-blue-700', label: '✏️ UPDATE' }, 
  DELETE: { bg: 'bg-red-100', text: 'text-red-700', label: '🗑️ DELETE' }, 
  MARK_PAID: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: '💰 PAID' }, 
  ARCHIVE: { bg: 'bg-orange-100', text: 'text-orange-700', label: '📦 ARCHIVE' }, 
} 

export default function AuditLogs() { 
  const { user, isAuthenticated, loading: authLoading } = useAuth() 
  const [logs, setLogs] = useState([]) 
  const [loading, setLoading] = useState(true) 
  const [error, setError] = useState(null) 
  const [search, setSearch] = useState('') 
  const [actionFilter, setActionFilter] = useState('all') 
  const [dateFilter, setDateFilter] = useState('') 

  const fetchLogs = async () => { 
    if (!isAuthenticated) return
    setLoading(true) 
    setError(null) 
    try { 
      const res = await audit.getLogs({
        search,
        action: actionFilter,
        date_from: dateFilter
      })

      if (res.ok && res.data) {
        setLogs(res.data || []) 
      } else {
        setError(res.error || 'Failed to load logs') 
      }
    } catch (e) { 
      setError('Failed to connect to server') 
    } 
    setLoading(false) 
  } 

  useEffect(() => { 
    if (!authLoading) {
      fetchLogs() 
    }
  }, [authLoading, isAuthenticated]) 

  const formatDate = (dt) => { 
    if (!dt) return '—' 
    const d = new Date(dt) 
    return d.toLocaleDateString('en-IN', { 
      day: '2-digit', month: 'short', year: 'numeric', 
      hour: '2-digit', minute: '2-digit' 
    }) 
  } 

  // Check admin access 
  const isAdmin = user?.role === 'MASTER_ADMIN' || user?.role === 'COMPANY_ADMIN' || user?.role === 'ADMIN' 
  
  if (authLoading) {
    return <div className="p-12 text-center text-gray-500">Authenticating...</div>
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen"> 
        <div className="text-center"> 
          <div className="text-6xl mb-4">🔑</div> 
          <h2 className="text-2xl font-bold text-gray-700">Login Required</h2> 
          <p className="text-gray-500 mt-2">Please log in to view audit logs</p>
          <button 
            onClick={() => window.location.href = '/auth/login'} 
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Log In
          </button>
        </div> 
      </div> 
    )
  }

  if (!isAdmin) { 
    return ( 
      <div className="flex items-center justify-center min-h-screen"> 
        <div className="text-center"> 
          <div className="text-6xl mb-4">🔒</div> 
          <h2 className="text-2xl font-bold text-gray-700">Access Denied</h2> 
          <p className="text-gray-500 mt-2">Only admins can view audit logs</p> 
        </div> 
      </div> 
    ) 
  } 

  return ( 
    <div className="max-w-7xl mx-auto p-6"> 
      {/* Header */} 
      <div className="mb-6"> 
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2"> 
          📋 System Audit Logs 
        </h1> 
        <p className="text-gray-500 text-sm mt-1"> 
          All PO actions — visible to admin team only 
        </p> 
      </div> 

      {/* Filters */} 
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6 flex flex-wrap gap-3 items-center"> 
        <input 
          type="text" 
          placeholder="Search by PO#, vendor, user or reason..." 
          value={search} 
          onChange={e => setSearch(e.target.value)} 
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm flex-1 min-w-48 focus:outline-none focus:ring-2 focus:ring-blue-500" 
        /> 
        <select 
          value={actionFilter} 
          onChange={e => setActionFilter(e.target.value)} 
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
        > 
          <option value="all">All Actions</option> 
          <option value="CREATE">Create</option> 
          <option value="UPDATE">Update</option> 
          <option value="DELETE">Delete</option> 
          <option value="MARK_PAID">Mark Paid</option> 
          <option value="ARCHIVE">Archive</option> 
        </select> 
        <input 
          type="date" 
          value={dateFilter} 
          onChange={e => setDateFilter(e.target.value)} 
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" 
        /> 
        <button 
          onClick={fetchLogs} 
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700" 
        > 
          Search 
        </button> 
        <button 
          onClick={() => { setSearch(''); setActionFilter('all'); setDateFilter('') }} 
          className="border border-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm hover:bg-gray-50" 
        > 
          Clear 
        </button> 
      </div> 

      {/* Stats */} 
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6"> 
        {Object.entries(ACTION_COLORS).map(([action, style]) => ( 
          <div key={action} className="bg-white rounded-lg p-3 shadow-sm text-center"> 
            <div className={`text-lg font-bold ${style.text}`}> 
              {logs.filter(l => l.action === action).length} 
            </div> 
            <div className="text-xs text-gray-500 mt-1">{style.label}</div> 
          </div> 
        ))} 
      </div> 

      {/* Table */} 
      {loading ? ( 
        <div className="text-center py-12"> 
          <div className="animate-spin text-4xl">⏳</div> 
          <p className="text-gray-500 mt-2">Loading audit logs...</p> 
        </div> 
      ) : error ? ( 
        <div className="bg-red-50 text-red-600 p-4 rounded-xl text-center"> 
          ❌ {error} 
          {error.toLowerCase().includes('token') || error.toLowerCase().includes('unauthorized') || error.toLowerCase().includes('authenticated') ? (
            <button 
              onClick={() => window.location.href = '/auth/login'} 
              className="ml-3 underline font-bold"
            >
              Log in again
            </button>
          ) : (
            <button onClick={fetchLogs} className="ml-3 underline">Retry</button>
          )}
        </div> 
      ) : logs.length === 0 ? ( 
        <div className="bg-white rounded-xl shadow-sm p-12 text-center text-gray-500"> 
          <div className="text-5xl mb-3">📭</div> 
          <p>No logs found. Try different filters.</p> 
        </div> 
      ) : ( 
        <div className="bg-white rounded-xl shadow-sm overflow-hidden"> 
          <div className="overflow-x-auto"> 
            <table className="w-full text-sm"> 
              <thead className="bg-gray-50 border-b border-gray-200"> 
                <tr> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">Date & Time</th> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">User</th> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">Action</th> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">PO #</th> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">Vendor</th> 
                  <th className="text-left px-4 py-3 text-gray-600 font-semibold">Reason</th> 
                </tr> 
              </thead> 
              <tbody className="divide-y divide-gray-100"> 
                {logs.map((log, i) => { 
                  const style = ACTION_COLORS[log.action] || { bg: 'bg-gray-100', text: 'text-gray-700', label: log.action } 
                  return ( 
                    <tr key={log.id || i} className="hover:bg-gray-50 transition-colors"> 
                      <td className="px-4 py-3 text-gray-500 whitespace-nowrap text-xs"> 
                        {formatDate(log.created_at)} 
                      </td> 
                      <td className="px-4 py-3"> 
                        <div className="font-medium text-gray-800">{log.user_name || '—'}</div> 
                        <div className="text-xs text-gray-400">{log.user_email || '—'}</div> 
                      </td> 
                      <td className="px-4 py-3"> 
                        <span className={`${style.bg} ${style.text} px-2 py-1 rounded-full text-xs font-semibold`}> 
                          {style.label} 
                        </span> 
                      </td> 
                      <td className="px-4 py-3 font-mono text-gray-700">{log.po_number || '—'}</td> 
                      <td className="px-4 py-3 text-gray-600">{log.vendor_name || '—'}</td> 
                      <td className="px-4 py-3 text-gray-500 max-w-xs truncate" title={log.reason}> 
                        {log.reason || '—'} 
                      </td> 
                    </tr> 
                  ) 
                })} 
              </tbody> 
            </table> 
          </div> 
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-500"> 
            Showing {logs.length} log{logs.length !== 1 ? 's' : ''} 
          </div> 
        </div> 
      )} 
    </div> 
  ) 
} 
