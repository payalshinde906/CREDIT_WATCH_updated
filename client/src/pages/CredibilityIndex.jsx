import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../state/authContext'
import { purchaseOrders, credibility } from '../services/api/apiClient'

export default function CredibilityIndex() {
  const { loading, user } = useAuth()
  const [poRows, setPoRows] = useState([])
  const [companies, setCompanies] = useState([])
  const [q, setQ] = useState('')
  const [risk, setRisk] = useState('')
  const [sort, setSort] = useState('desc')

  useEffect(() => {
    async function loadPOs() {
      try {
        const res = await purchaseOrders.list(1, 1000, true)
        const items = Array.isArray(res?.data?.items) ? res.data.items : Array.isArray(res?.data) ? res.data : []
        setPoRows(items)
      } catch {
        setPoRows([])
      }
    }
    loadPOs()
    const onChanged = () => loadPOs()
    window.addEventListener('poChanged', onChanged)
    return () => window.removeEventListener('poChanged', onChanged)
  }, [user])

  useEffect(() => { 
    async function loadFromBackend() { 
      try { 
        const res = await credibility.list()
        if (res.ok && Array.isArray(res.data)) { 
          setCompanies(res.data) 
        } 
      } catch (err) { 
        console.error( 
          'Credibility fetch error:', 
          err 
        ) 
      } 
    } 
    loadFromBackend() 
  }, [user]) 

  const computedCompanies = useMemo(() => {
    // Note: Main logic moved to backend, this is for fallback/compatibility
    const byVendor = new Map()
    for (const po of poRows) {
      const vendor = (po.vendor || '').trim()
      if (!vendor) continue
      const arr = byVendor.get(vendor) || []
      arr.push(po)
      byVendor.set(vendor, arr)
    }
    const toMetrics = (vendorPOs) => {
      const total = vendorPOs.length
      const paid = vendorPOs.filter(p => p.payment_completed_at || String(p.status || '').toLowerCase() === 'closed').length
      const pending = vendorPOs.filter(p => {
        const s = String(p.status || '').toLowerCase()
        return s.includes('open') || s.includes('pending')
      }).length
      const score = total ? Math.round((paid / total) * 100) : 0
      let grade = 'D'
      if (score >= 90) grade = 'A'
      else if (score >= 75) grade = 'B'
      else if (score >= 50) grade = 'C'
      const risk = score >= 80 ? 'Low' : score >= 50 ? 'Medium' : 'High'
      
      // Star rating calculation based on SOP rules
      const percentage = total ? (paid / total) * 100 : 0
      let stars = 1
      if (percentage >= 90) stars = 5
      else if (percentage >= 75) stars = 4
      else if (percentage >= 60) stars = 3
      else if (percentage >= 40) stars = 2
      
      return { total, paid, pending, score, grade, risk, stars }
    }
    const out = []
    for (const [vendor, vpos] of byVendor.entries()) {
      const m = toMetrics(vpos)
      out.push({
        company_id: null,
        company_name: vendor,
        ...m,
      })
    }
    return out
  }, [poRows])

  if (loading) return <div className="p-6">Loading...</div>

  let filtered = companies.filter(r => r.company_name.toLowerCase().includes(q.toLowerCase()))
  if (risk) filtered = filtered.filter(r => String((r.risk || r.risk_level) || '').toLowerCase() === risk.toLowerCase())
  filtered.sort((a, b) => (sort === 'asc' ? (a.score || 0) - (b.score || 0) : (b.score || 0) - (a.score || 0)))

  return (
    <section className="section-padding">
      <div className="container-custom space-y-6">
        <h1 className="text-3xl font-heading font-bold text-gray-900">Business Credibility Index</h1>
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-full bg-amber-400 text-white flex items-center justify-center" title="Credibility Index">★</div>
              <p className="text-xl font-heading font-bold text-amber-900">Business Credibility Index</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search company" className="input" />
            <select value={risk} onChange={e => setRisk(e.target.value)} className="input">
              <option value="">All risks</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
            <select value={sort} onChange={e => setSort(e.target.value)} className="input">
              <option value="desc">Top score</option>
              <option value="asc">Lowest score</option>
            </select>
          </div>
        </div>
        <div className="card">
          <table className="w-full">
            <thead>
              <tr>
                <th className="text-left p-2">Company</th>
                <th className="text-left p-2">Score</th>
                <th className="text-left p-2">Grade</th>
                <th className="text-left p-2">Risk</th>
                <th className="text-left p-2">PO Fulfillment</th>
                <th className="text-left p-2">Performance</th>
                <th className="text-left p-2">View</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(r => (
                <tr key={r.company_name}>
                  <td className="p-2">{r.company_name}</td>
                  <td className="p-2">
                    <div className="flex items-center gap-2" title="Score out of 100">
                      <div className="w-24 h-1.5 bg-gray-100 rounded overflow-hidden">
                        <div className={`${r.score >= 70 ? 'bg-emerald-500' : r.score >= 40 ? 'bg-amber-500' : 'bg-red-500'} h-full`} style={{ width: `${Math.max(0, Math.min(100, r.score || 0))}%` }} />
                      </div>
                      <span className="text-xs text-gray-700">{r.score ?? 0}</span>
                    </div>
                  </td>
                  <td className="p-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-semibold ${r.grade === 'A' ? 'bg-emerald-100 text-emerald-800' : r.grade === 'B' ? 'bg-blue-100 text-blue-800' : r.grade === 'C' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}
                      title="Grade calculation factors on-time rate and delays"
                    >
                      {r.grade}
                    </span>
                  </td>
                  <td className="p-2" title="Risk level bands">
                    <span className={`${(r.risk || r.risk_level) === 'Low' ? 'text-emerald-600' : (r.risk || r.risk_level) === 'Medium' ? 'text-amber-600' : 'text-red-600'}`}>
                      {(r.risk || r.risk_level) === 'Low' ? '✅ Low' : (r.risk || r.risk_level) === 'Medium' ? '⚠️ Medium' : '❌ High'}
                    </span>
                  </td>
                  <td className="p-2">
                    <div title="Green: Paid, Amber: Pending" className="min-w-[180px]">
                      <div className="w-full h-2 rounded bg-gray-100 overflow-hidden">
                        <div className="h-full bg-emerald-500 inline-block" style={{ width: `${r.total_pos ? Math.round((r.paid_pos / r.total_pos) * 100) : 0}%` }} />
                        <div className="h-full bg-amber-500 inline-block" style={{ width: `${r.total_pos ? Math.round((r.unpaid / r.total_pos) * 100) : 0}%` }} />
                      </div>
                      <div className="text-xs text-gray-700 mt-1">{r.paid_pos}/{r.total_pos} Paid</div>
                    </div>
                  </td>
                  <td className="p-2">
                    <div aria-label="Performance rating" title="Based on ratio of paid to total POs">
                      {'★★★★★'.slice(0, r.stars)}<span className="text-gray-300">{'★★★★★'.slice(r.stars)}</span>
                    </div>
                  </td>
                  <td className="p-2">
                    <Link 
                      to={`/credibility-index/${r.company_id}`} 
                      className="text-primary-700 font-medium hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
