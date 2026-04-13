import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../state/authContext'
import { purchaseOrders, credibility, ratings } from '../services/api/apiClient'

function StarDisplay({ stars, color = "text-amber-500" }) {
  const s = Math.round(stars || 0)
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <span key={i} className={i <= s ? color : "text-gray-200"}>★</span>
      ))}
    </div>
  )
}

export default function CredibilityIndex() {
  const { loading, user } = useAuth()
  const [poRows, setPoRows] = useState([])
  const [companies, setCompanies] = useState([])
  const [globalCbi, setGlobalCbi] = useState([])
  const [q, setQ] = useState('')
  const [risk, setRisk] = useState('')
  const [sort, setSort] = useState('desc')
  const [aiTrends, setAiTrends] = useState('')

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
        
        const cbiRes = await ratings.getGlobalCbi()
        if (cbiRes.ok && Array.isArray(cbiRes.data)) {
          setGlobalCbi(cbiRes.data)
        }

        const trendsRes = await ratings.getAiTrends()
        if (trendsRes.ok) {
          setAiTrends(trendsRes.data.summary)
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

        {aiTrends && (
          <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5 shadow-sm">
            <h2 className="text-lg font-bold text-blue-900 mb-2">AI Platform Insights</h2>
            <p className="text-blue-800 text-sm italic">"{aiTrends}"</p>
          </div>
        )}

        <div className="grid gap-8">
          {/* Section 1: Local CBI */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-800">Direct Trade Reliability (Local CBI)</h2>
            <p className="text-sm text-gray-500">Credibility based on your direct business history with these companies.</p>
            <div className="card">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="text-left p-2">Company</th>
                    <th className="text-left p-2">Performance</th>
                    <th className="text-left p-2">Grade</th>
                    <th className="text-left p-2">Risk</th>
                    <th className="text-left p-2">PO Fulfillment</th>
                    <th className="text-left p-2">View</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr><td colSpan="6" className="p-4 text-center text-gray-500">No local business history found.</td></tr>
                  ) : (
                    filtered.map(r => (
                      <tr key={r.company_name}>
                        <td className="p-2 font-medium">{r.company_name}</td>
                        <td className="p-2">
                          <StarDisplay stars={r.stars} color="text-emerald-500" />
                        </td>
                        <td className="p-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${r.grade === 'A' ? 'bg-emerald-100 text-emerald-800' : r.grade === 'B' ? 'bg-blue-100 text-blue-800' : r.grade === 'C' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}>
                            {r.grade}
                          </span>
                        </td>
                        <td className="p-2">
                          <span className={`${(r.risk || r.risk_level) === 'Low' ? 'text-emerald-600' : (r.risk || r.risk_level) === 'Medium' ? 'text-amber-600' : 'text-red-600'}`}>
                            {(r.risk || r.risk_level) === 'Low' ? '✅ Low' : (r.risk || r.risk_level) === 'Medium' ? '⚠️ Medium' : '❌ High'}
                          </span>
                        </td>
                        <td className="p-2">
                          <div className="min-w-[180px]">
                            <div className="w-full h-2 rounded bg-gray-100 overflow-hidden">
                              <div className="h-full bg-emerald-500 inline-block" style={{ width: `${r.total_pos ? Math.round((r.paid_pos / r.total_pos) * 100) : 0}%` }} />
                              <div className="h-full bg-amber-500 inline-block" style={{ width: `${r.total_pos ? Math.round((r.unpaid / r.total_pos) * 100) : 0}%` }} />
                            </div>
                            <div className="text-xs text-gray-700 mt-1">{r.paid_pos}/{r.total_pos} Paid</div>
                          </div>
                        </td>
                        <td className="p-2">
                          <Link to={`/credibility-index/${r.company_id}`} className="text-primary-700 font-medium hover:underline">View</Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 2: Global CBI */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-800">Network Trust Intelligence</h2>
            <p className="text-sm text-gray-500">Average credibility ratings from across the entire CreditDataWatch platform.</p>
            <div className="card">
              <table className="w-full">
                <thead> 
                  <tr> 
                    <th className="text-left p-2">Company</th> 
                    <th className="text-left p-2">Partner Trust Score</th> 
                    <th className="text-left p-2">AI Credit Risk Verdict</th> 
                    <th className="text-left p-2">Status</th> 
                  </tr> 
                </thead> 
                <tbody> 
                  {globalCbi.filter(c => c.company_name.toLowerCase().includes(q.toLowerCase())).length === 0 ? ( 
                    <tr><td colSpan="4" className="p-4 text-center text-gray-500">No platform data available.</td></tr> 
                  ) : ( 
                    globalCbi.filter(c => c.company_name.toLowerCase().includes(q.toLowerCase())).map(c => { 
                      const stars = c.global_cbi_stars || 0 
                      const assessment = stars >= 4 
                        ? { label: 'Low Risk', color: 'text-emerald-700', bg: 'bg-emerald-50', icon: '✅' } 
                        : stars >= 3 
                        ? { label: 'Moderate Risk', color: 'text-amber-700', bg: 'bg-amber-50', icon: '⚠️' } 
                        : stars >= 1 
                        ? { label: 'High Risk', color: 'text-red-700', bg: 'bg-red-50', icon: '❌' } 
                        : { label: 'Not Rated', color: 'text-gray-500', bg: 'bg-gray-50', icon: '—' } 
                      return ( 
                        <tr key={c.id} className="border-t border-gray-100 hover:bg-gray-50"> 
                          <td className="p-3 font-medium text-gray-800">{c.company_name}</td> 
                          <td className="p-3"> 
                            <div className="flex items-center gap-2"> 
                              <div className="flex gap-0.5"> 
                                {[1,2,3,4,5].map(i => { 
                                  const full = i <= Math.floor(stars) 
                                  const half = !full && i === Math.ceil(stars) && stars % 1 >= 0.25 
                                  return ( 
                                    <span key={i} className="text-base relative" style={{display:'inline-block',width:'1.1em'}}> 
                                      <span className="text-gray-200">★</span> 
                                      {(full || half) && ( 
                                        <span className="absolute left-0 top-0 text-amber-400 overflow-hidden" 
                                          style={{width: full ? '100%' : '50%'}}>★</span> 
                                      )} 
                                    </span> 
                                  ) 
                                })} 
                              </div> 
                              <span className="text-sm font-bold text-amber-500">{stars.toFixed(1)}</span> 
                            </div> 
                          </td> 
                          <td className="p-3"> 
                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold ${assessment.bg} ${assessment.color}`}> 
                              {assessment.icon} {assessment.label} 
                            </span> 
                          </td> 
                          <td className="p-3"> 
                            {c.is_verified 
                              ? <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">Verified</span> 
                              : <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">Standard</span> 
                            } 
                          </td> 
                        </tr> 
                      ) 
                    }) 
                  )} 
                </tbody> 
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
