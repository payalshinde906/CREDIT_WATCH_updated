import { useState } from 'react'
import { motion } from 'framer-motion'
import { contact as contactApi } from '../services/api/apiClient'
import { Link } from 'react-router-dom'

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', message: '' })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)

    const res = await contactApi.submit(form)
    
    if (res.ok) {
      setSuccess(true)
      setForm({ name: '', email: '', message: '' })
    } else {
      setError(res.error || 'Failed to send message. Please try again.')
    }
    
    setLoading(false)
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Contact</h1>
          <p className="text-lg text-gray-600 mb-6">Tell us about your credit workflows and we will tailor a walkthrough.</p>
          
          {/* Success Message */}
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 bg-green-50 border-2 border-green-300 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2"
            >
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-semibold">Message sent successfully!</p>
                <p className="text-sm">Thank you for contacting us. We will respond within 24 hours.</p>
              </div>
            </motion.div>
          )}

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 bg-red-50 border-2 border-red-300 text-red-800 px-4 py-3 rounded-lg flex items-center gap-2"
            >
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-semibold">Failed to send message</p>
                <p className="text-sm">{error}</p>
              </div>
            </motion.div>
          )}

          {/* Appointment CTA */}
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Need immediate assistance?</h3>
            <p className="text-sm text-blue-700 mb-3">
              Schedule a consultation with our credit specialists to discuss your specific needs.
            </p>
            <Link to="/appointment" className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Book an Appointment →
            </Link>
          </div>

          <div className="card">
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="name" className="text-sm font-semibold text-gray-700">Name</label>
                <input
                  id="name"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label htmlFor="email" className="text-sm font-semibold text-gray-700">Email</label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  placeholder="you@company.com"
                />
              </div>
              <div>
                <label htmlFor="message" className="text-sm font-semibold text-gray-700">Message</label>
                <textarea
                  id="message"
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  required
                  rows={5}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  placeholder="What do you want to achieve?"
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
