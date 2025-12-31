import { useState } from 'react'
import { motion } from 'framer-motion'

export default function Contact() {
  const [form, setForm] = useState({ name: '', email: '', message: '' })

  const handleSubmit = (e) => {
    e.preventDefault()
    // placeholder action
    alert('Thanks for reaching out! We will respond shortly.')
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
              <button type="submit" className="btn-primary w-full">Send</button>
            </form>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
