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
            <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              Thank you for contacting us! We will respond within 24 hours.
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
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
