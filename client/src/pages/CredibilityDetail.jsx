

import { useEffect, useState } from 'react' 
import { useParams } from 'react-router-dom' 
import { useAuth } from '../state/authContext' 

const GRADE_COLOR = { 
  A: 'bg-green-100 text-green-700', 
  B: 'bg-blue-100 text-blue-700', 
  C: 'bg-yellow-100 text-yellow-700', 
  D: 'bg-red-100 text-red-700', 
} 

const RISK_COLOR = { 
  Low: 'bg-green-100 text-green-700', 
  Medium: 'bg-yellow-100 text-yellow-700', 
  High: 'bg-red-100 text-red-700', 
} 

function StarRating({ stars }) { 
  return ( 
    <div className="flex gap-1"> 
      {[1,2,3,4,5].map(i => ( 
        <span key={i} 
          className={`text-xl ${ 
            i <= stars 
              ? 'text-yellow-400' 
              : 'text-gray-200' 
          }`}>★</span> 
      ))} 
    </div> 
  ) 
} 

function ScoreRing({ score, grade }) { 
  const radius = 40 
  const circ = 2 * Math.PI * radius 
  const offset = circ - 
    (score / 100) * circ 
  const color = 
    score >= 75 ? '#22c55e' : 
    score >= 50 ? '#f59e0b' : '#ef4444' 
  return ( 
    <div className="relative 
      flex items-center 
      justify-center w-28 h-28"> 
      <svg className="absolute 
        -rotate-90" 
        width="112" height="112"> 
        <circle cx="56" cy="56" 
          r={radius} 
          fill="none" 
          stroke="#e5e7eb" 
          strokeWidth="10"/> 
        <circle cx="56" cy="56" 
          r={radius} 
          fill="none" 
          stroke={color} 
          strokeWidth="10" 
          strokeDasharray={circ} 
          strokeDashoffset={offset} 
          strokeLinecap="round"/> 
      </svg> 
      <div className="text-center 
        z-10"> 
        <div className="text-2xl 
          font-bold text-gray-800"> 
          {score} 
        </div> 
        <div className={`text-xs 
          font-bold px-2 py-0.5 
          rounded-full mt-1 
          ${GRADE_COLOR[grade] || 
            'bg-gray-100 text-gray-600' 
          }`}> 
          {grade} 
        </div> 
      </div> 
    </div> 
  ) 
} 

export default function 
CredibilityDetail() { 
  const { companyId } = useParams() 
  const { loading: authLoading } = 
    useAuth() 
  const [data, setData] = useState(null) 
  const [activeTab, setActiveTab] = 
    useState('overview') 
  const [aiAnalysis, setAiAnalysis] = 
    useState(null) 
  const [loadingAi, setLoadingAi] = 
    useState(false) 
  const [aiRec, setAiRec] = 
    useState(null) 
  const [loadingRec, setLoadingRec] = 
    useState(false) 

  useEffect(() => { 
    async function load() { 
      try { 
        const res = await fetch( 
          `http://localhost:8000/api/v1/credibility/${companyId}`, 
          { credentials: 'include' } 
        ) 
        const json = await res.json() 
        if (json.success) { 
          setData(json.data || null) 
        } 
      } catch (err) { 
        console.error('Load error:', err) 
      } 
    } 
    load() 
  }, [companyId]) 

  const fetchAiAnalysis = async () => { 
    if (aiAnalysis) return 
    setLoadingAi(true) 
    try { 
      const res = await fetch( 
        `/api/v1/credibility/${companyId}/ai-analysis`, 
        { 
          method: 'POST', 
          credentials: 'include' 
        } 
      ) 
      const json = await res.json() 
      if (json.success) { 
        setAiAnalysis(json.data) 
      } 
    } catch (err) { 
      console.error('AI error:', err) 
    } finally { 
      setLoadingAi(false) 
    } 
  } 

  const fetchAiRecommendation = 
    async (d) => { 
    if (aiRec || !d) return 
    setLoadingRec(true) 
    try { 
      const res = await fetch( 
        `http://localhost:8000/api/v1/credibility/${companyId}/ai-analysis`, 
        { 
          method: 'POST', 
          credentials: 'include', 
          headers: { 'Content-Type': 'application/json' } 
        } 
      ) 
      const json = await res.json() 
      if (json.success && json.data) { 
        setAiRec({ 
          verdict: json.data.verdict, 
          reasons: json.data.analysis_points || [] 
        }) 
      } 
    } catch (err) { 
      console.error('Rec error:', err) 
    } finally { 
      setLoadingRec(false) 
    } 
  } 

  useEffect(() => { 
    if (data) { 
      fetchAiRecommendation(data) 
    } 
  }, [data]) 

  useEffect(() => { 
    if (activeTab === 'ai-report') { 
      fetchAiAnalysis() 
    } 
  }, [activeTab]) 

  if (authLoading || !data) return ( 
    <div className="flex items-center 
      justify-center min-h-[400px]"> 
      <div className="h-12 w-12 
        animate-spin rounded-full 
        border-4 border-blue-100 
        border-t-blue-600" /> 
    </div> 
  ) 

  const m = data.metrics 
  const fulfillPct = m.fulfillment_rate 

  const VERDICT_STYLE = { 
    'RECOMMENDED TO DEAL WITH': 
      'bg-green-50 border-green-300 text-green-700', 
    'PROCEED WITH CAUTION': 
      'bg-yellow-50 border-yellow-300 text-yellow-700', 
    'NOT RECOMMENDED': 
      'bg-red-50 border-red-300 text-red-700', 
  } 

  return ( 
    <div className="max-w-5xl mx-auto 
      px-4 py-6"> 
 
       {/* Header */} 
       <div className="mb-6"> 
         <h1 className="text-2xl 
           font-bold text-gray-800"> 
           {data.company_name} 
         </h1> 
         <p className="text-gray-500 
           text-sm mt-1"> 
           Credibility Detail Report 
         </p> 
       </div> 
 
       {/* 5 Metric Cards */} 
       <div className="grid grid-cols-2 
         md:grid-cols-5 gap-4 mb-6"> 
 
         {/* Card 1 — Credit Score */} 
         <div className="bg-white 
           rounded-xl shadow-sm border 
           p-4 flex flex-col 
           items-center"> 
           <p className="text-xs 
             text-gray-500 mb-2 
             font-medium"> 
             Credit Score 
           </p> 
           <ScoreRing 
             score={data.score} 
             grade={data.grade} 
           /> 
         </div> 
 
         {/* Card 2 — Risk Level */} 
         <div className="bg-white 
           rounded-xl shadow-sm border 
           p-4 flex flex-col 
           items-center justify-center"> 
           <p className="text-xs 
             text-gray-500 mb-2 
             font-medium"> 
             Risk Level 
           </p> 
           <span className={`px-3 py-1 
             rounded-full text-sm 
             font-bold ${ 
               RISK_COLOR[ 
                 data.risk_level 
               ] || 
               'bg-gray-100 text-gray-600' 
             }`}> 
             {data.risk_level} 
           </span> 
           <p className="text-xs 
             text-gray-400 mt-2 
             text-center"> 
             Based on payment history 
           </p> 
         </div> 
 
         {/* Card 3 — PO Fulfillment */} 
         <div className="bg-white 
           rounded-xl shadow-sm border 
           p-4 flex flex-col 
           items-center justify-center"> 
           <p className="text-xs 
             text-gray-500 mb-2 
             font-medium"> 
             PO Fulfillment 
           </p> 
           <p className="text-xl 
             font-bold text-gray-800"> 
             {m.paid_on_time}/ 
             {m.total_pos} 
           </p> 
           <div className="w-full 
             bg-gray-100 rounded-full 
             h-2 mt-2"> 
             <div 
               className="bg-green-500 
                 h-2 rounded-full" 
               style={{ 
                 width: `${fulfillPct}%` 
               }} 
             /> 
           </div> 
           <p className="text-xs 
             text-gray-400 mt-1"> 
             {fulfillPct}% paid on time 
           </p> 
         </div> 
 
         {/* Card 4 — Performance */} 
         <div className="bg-white 
           rounded-xl shadow-sm border 
           p-4 flex flex-col 
           items-center justify-center"> 
           <p className="text-xs 
             text-gray-500 mb-2 
             font-medium"> 
             Performance 
           </p> 
           <StarRating 
             stars={data.stars} 
           /> 
           <p className="text-xs 
             text-gray-400 mt-2"> 
             {data.stars}/5 stars 
           </p> 
         </div> 
 
         {/* Card 5 — Credit Limit */} 
         <div className="bg-white 
           rounded-xl shadow-sm border 
           p-4 flex flex-col 
           items-center justify-center"> 
           <p className="text-xs 
             text-gray-500 mb-2 
             font-medium"> 
             Credit Limit 
           </p> 
           <p className="text-lg 
             font-bold text-gray-800"> 
             {data.score >= 75 
               ? '₹5,00,000' 
               : data.score >= 50 
               ? '₹2,00,000' 
               : '₹50,000'} 
           </p> 
           <p className="text-xs 
             text-gray-400 mt-1"> 
             {data.score >= 75 
               ? 'Net 30' 
               : data.score >= 50 
               ? 'Net 15' 
               : 'Advance Only'} 
           </p> 
         </div> 
       </div> 
 
       {/* Tabs */} 
       <div className="flex gap-2 
         mb-4 border-b"> 
         {['overview', 
           'financials', 
           'ai-report' 
         ].map(tab => ( 
           <button 
             key={tab} 
             onClick={() => 
               setActiveTab(tab)} 
             className={`px-4 py-2 
               text-sm font-medium 
               capitalize border-b-2 
               transition-colors ${ 
               activeTab === tab 
                 ? 'border-blue-600 text-blue-600' 
                 : 'border-transparent text-gray-500 hover:text-gray-700' 
             }`} 
           > 
             {tab === 'ai-report' 
               ? 'AI Report' 
               : tab.charAt(0) 
                   .toUpperCase() + 
                 tab.slice(1)} 
           </button> 
         ))} 
       </div> 
 
       {/* Tab Content */} 
       <div className="bg-white 
         rounded-xl shadow-sm border 
         p-6 mb-6"> 
 
         {/* Overview Tab */} 
         {activeTab === 'overview' && ( 
           <div className="grid 
             md:grid-cols-2 gap-6"> 
             <div> 
               <h3 className="font-bold 
                 text-gray-700 mb-3"> 
                 Company Details 
               </h3> 
               <div className="space-y-2 
                 text-sm"> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Company 
                   </span> 
                   <span className= 
                     "font-medium"> 
                     {data.company_name} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Grade 
                   </span> 
                   <span className={` 
                     px-2 py-0.5 
                     rounded-full 
                     text-xs font-bold 
                     ${GRADE_COLOR[ 
                       data.grade 
                     ]}`}> 
                     {data.grade} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Risk 
                   </span> 
                   <span className={` 
                     px-2 py-0.5 
                     rounded-full 
                     text-xs font-bold 
                     ${RISK_COLOR[ 
                       data.risk_level 
                     ]}`}> 
                     {data.risk_level} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Last Updated 
                   </span> 
                   <span className= 
                     "font-medium"> 
                     {data 
                       .last_calculated_at 
                       ? new Date( 
                           data.last_calculated_at 
                         ).toLocaleDateString() 
                       : 'N/A'} 
                   </span> 
                 </div> 
               </div> 
             </div> 
             <div> 
               <h3 className="font-bold 
                 text-gray-700 mb-3"> 
                 Credit Summary 
               </h3> 
               <div className="space-y-2 
                 text-sm"> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Total POs 
                   </span> 
                   <span className= 
                     "font-medium"> 
                     {m.total_pos} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Paid On Time 
                   </span> 
                   <span className= 
                     "font-medium 
                     text-green-600"> 
                     {m.paid_on_time} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Unpaid 
                   </span> 
                   <span className= 
                     "font-medium 
                     text-red-500"> 
                     {m.unpaid} 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Avg Delay 
                   </span> 
                   <span className= 
                     "font-medium"> 
                     {m.avg_delay_days 
                       || 0} days 
                   </span> 
                 </div> 
                 <div className="flex 
                   justify-between"> 
                   <span className= 
                     "text-gray-500"> 
                     Fulfillment Rate 
                   </span> 
                   <span className= 
                     "font-medium 
                     text-blue-600"> 
                     {fulfillPct}% 
                   </span> 
                 </div> 
               </div> 
             </div> 
           </div> 
         )} 
 
         {/* Financials Tab */} 
         {activeTab === 'financials' && ( 
           <div> 
             <h3 className="font-bold 
               text-gray-700 mb-4"> 
               Financial Overview 
             </h3> 
             <div className="grid 
               grid-cols-2 md:grid-cols-4 
               gap-4"> 
               {[ 
                 { 
                   label: 'Total POs', 
                   value: m.total_pos, 
                   color: 'text-gray-800' 
                 }, 
                 { 
                   label: 'Paid', 
                   value: m.paid_on_time, 
                   color: 'text-green-600' 
                 }, 
                 { 
                   label: 'Unpaid', 
                   value: m.unpaid, 
                   color: 'text-red-500' 
                 }, 
                 { 
                   label: 'Avg Delay', 
                   value: `${m.avg_delay_days || 0}d`, 
                   color: 'text-yellow-600' 
                 }, 
               ].map(item => ( 
                 <div key={item.label} 
                   className="bg-gray-50 
                     rounded-lg p-4 
                     text-center"> 
                   <p className={`text-2xl 
                     font-bold 
                     ${item.color}`}> 
                     {item.value} 
                   </p> 
                   <p className="text-xs 
                     text-gray-500 mt-1"> 
                     {item.label} 
                   </p> 
                 </div> 
               ))} 
             </div> 
           </div> 
         )} 
 
         {/* AI Report Tab */} 
         {activeTab === 'ai-report' && ( 
           <div> 
             <div className="flex 
               justify-between 
               items-center mb-4"> 
               <h3 className="font-bold 
                 text-gray-700"> 
                 AI Credit Report 
               </h3> 
               <button 
                 onClick={fetchAiAnalysis} 
                 disabled={loadingAi} 
                 className="px-4 py-2 
                   bg-blue-600 text-white 
                   rounded-lg text-sm 
                   hover:bg-blue-700 
                   disabled:opacity-50" 
               > 
                 {loadingAi 
                   ? 'Generating...' 
                   : aiAnalysis 
                   ? 'Regenerate' 
                   : 'Generate Report'} 
               </button> 
             </div> 
 
             {loadingAi && ( 
               <div className="flex 
                 items-center 
                 justify-center py-12"> 
                 <div className="h-8 w-8 
                   animate-spin 
                   rounded-full border-4 
                   border-blue-100 
                   border-t-blue-600"/> 
                 <span className="ml-3 
                   text-gray-500"> 
                   Generating AI report... 
                 </span> 
               </div> 
             )} 
 
             {aiAnalysis && 
              !loadingAi && ( 
               <div className="grid 
                 md:grid-cols-2 
                 gap-4"> 
                 {Object.entries( 
                   aiAnalysis 
                 ).map(([key, val]) => ( 
                   <div key={key} 
                     className="bg-gray-50 
                       rounded-lg p-4 
                       border"> 
                     <h4 className="font-bold 
                       text-gray-700 
                       text-sm mb-2 
                       capitalize"> 
                       {key.replace 
                         (/_/g, ' ')} 
                     </h4> 
                     <p className="text-sm 
                       text-gray-600 
                       leading-relaxed"> 
                       {typeof val === 
                         'string' 
                         ? val 
                         : JSON.stringify( 
                             val 
                           )} 
                     </p> 
                   </div> 
                 ))} 
               </div> 
             )} 
 
             {!aiAnalysis && !loadingAi && ( <p className="text-gray-400 text-center py-8"> Click Generate Report to see AI analysis </p> )} </div> )} </div> {/* AI Recommendation Section */} <div className="bg-white rounded-xl shadow-sm border p-6"> <h3 className="font-bold text-gray-700 mb-4"> 🤖 AI Recommendation </h3> {loadingRec && ( <div className="flex items-center gap-3 text-gray-500"> <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-100 border-t-blue-600"/> Analyzing vendor data... </div> )} {aiRec && !loadingRec && ( <div className={`border rounded-lg p-4 ${VERDICT_STYLE[ aiRec.verdict ] || 'bg-gray-50 border-gray-200' }`}> <p className="font-bold text-lg mb-3"> {aiRec.verdict === 'RECOMMENDED TO DEAL WITH' ? '✅' : aiRec.verdict === 'PROCEED WITH CAUTION' ? '⚠️' : '❌' } {aiRec.verdict} </p> <ul className="space-y-2"> {(aiRec.reasons || []) .map((r, i) => ( <li key={i} className="flex items-start gap-2 text-sm"> <span>•</span> <span>{r}</span> </li> ))} </ul> </div> )} {!aiRec && !loadingRec && ( <p className="text-gray-400 text-sm"> AI recommendation will appear automatically based on vendor data. </p> )} </div> </div> ) }