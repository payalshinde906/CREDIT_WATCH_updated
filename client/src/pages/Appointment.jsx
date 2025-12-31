import { useState } from 'react'
import { motion } from 'framer-motion'

export default function Appointment() {
  const [form, setForm] = useState({
    company: '',
    email: '',
    phone: '',
    gstin: '',
    topic: 'overdue',
    date: '',
    notes: '',
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    alert('Appointment request submitted!')
  }

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom max-w-4xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-4xl font-heading font-bold mb-4">Book Appointment</h1>
          <p className="text-lg text-gray-600 mb-8">Schedule a walkthrough with our credit specialists.</p>
          <div className="card">
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="company" className="text-sm font-semibold text-gray-700">Company / Legal Name</label>
                  <input
                    id="company"
                    name="company"
                    value={form.company}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label htmlFor="gstin" className="text-sm font-semibold text-gray-700">GSTIN (mandatory)</label>
                  <input
                    id="gstin"
                    name="gstin"
                    value={form.gstin}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    placeholder="22AAAAA0000A1Z5"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="email" className="text-sm font-semibold text-gray-700">Work Email</label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label htmlFor="phone" className="text-sm font-semibold text-gray-700">Phone</label>
                  <input
                    id="phone"
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="topic" className="text-sm font-semibold text-gray-700">Topic</label>
                  <select
                    id="topic"
                    name="topic"
                    value={form.topic}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  >
                    <option value="overdue">Report Overdue</option>
                    <option value="credit">Credit Management</option>
                    <option value="partners">Partners Overdue Report</option>
                    <option value="finalization">Finalization Steps</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="date" className="text-sm font-semibold text-gray-700">Preferred Date</label>
                  <input
                    id="date"
                    type="date"
                    name="date"
                    value={form.date}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="notes" className="text-sm font-semibold text-gray-700">Notes</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={form.notes}
                  onChange={handleChange}
                  rows={4}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                  placeholder="Share your current collections workflow, tools, and expected outcomes"
                />
              </div>

              <button type="submit" className="btn-primary w-full">Submit</button>
            </form>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
