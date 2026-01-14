import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { cms } from '../services/api/apiClient'
import PricingTable from '../components/cms/PricingTable'

const DEFAULT_CONTENT = {
  title: "Our Offerings",
  subtitle: "Scalable solutions for every stage of growth",
  plans: [
    {
      name: "Base",
      price: "₹500",
      description: "Entry-level plan for small businesses.",
      features: [
        "Validity: 1 Month",
        "Legal Assistance: NO",
        "Reminder Follow-ups: Yes",
        "CIR Generation Fee: Included"
      ]
    },
    {
      name: "Royal",
      price: "₹1,000",
      description: "For growing businesses.",
      features: [
        "Validity: 6 Months",
        "Legal Assistance: 5 Incidents",
        "Reminder Follow-ups: Yes",
        "CIR Generation Fee: Included"
      ]
    },
    {
      name: "Groups",
      price: "₹2,000",
      description: "For organizations with multiple entities.",
      features: [
        "Validity: 1 Year",
        "Legal Assistance: 20 Incidents",
        "Reminder Follow-ups: Yes",
        "CIR Generation Fee: Included"
      ]
    },
    {
      name: "Enterprise",
      price: "₹1,00,000",
      description: "Maximum protection and support.",
      features: [
        "Validity: 1 Year",
        "Legal Assistance: 100 Incidents",
        "Reminder Follow-ups: Yes",
        "CIR Generation Fee: Included"
      ]
    }
  ]
}

export default function Offerings() {
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchContent() {
      try {
        const res = await cms.getPage('offerings')
        // Check if page has a table section
        if (res.ok && res.data.sections) {
          const tableSection = res.data.sections.find(s => s.type === 'pricing_table')
          if (tableSection) {
            setContent(tableSection.content)
            setLoading(false)
            return
          }
        }
      } catch (e) {
        console.error("Failed to load offerings CMS", e)
      }
      // Fallback
      setContent(DEFAULT_CONTENT)
      setLoading(false)
    }
    fetchContent()
  }, [])

  if (loading) return <div className="p-10 text-center">Loading offerings...</div>

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <PricingTable content={content} />
    </motion.div>
  )
}
