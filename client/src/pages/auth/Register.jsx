import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function Register() {
  const [form, setForm] = useState({
    company: '',
    email: '',
    password: '',
    confirm: '',
    phone: '',
    gstin: '',
    accepts: false,
  })

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm({ ...form, [e.target.name]: value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) {
      alert('Passwords do not match')
      return
    }
    alert('Registration submitted (stub). GST validation will be enforced server-side.')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 justify-center mb-3">
            <div className="h-10 w-10 rounded-xl bg-primary-600 text-white font-heading font-bold text-xl flex items-center justify-center">CD</div>
            <span className="font-heading font-bold text-2xl text-gray-900">CreditDataWatch</span>
          </Link>
          <h1 className="text-3xl font-heading font-bold">Register</h1>
          <p className="text-gray-600">GST-validated access for businesses</p>
        </div>
        <div className="card">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="grid md:grid-cols-2 gap-4">
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
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="password" className="text-sm font-semibold text-gray-700">Password</label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
              </div>
              <div>
                <label htmlFor="confirm" className="text-sm font-semibold text-gray-700">Confirm Password</label>
                <input
                  id="confirm"
                  type="password"
                  name="confirm"
                  value={form.confirm}
                  onChange={handleChange}
                  required
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
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
                <p className="text-xs text-gray-500 mt-1">GSTIN will be validated and revalidated periodically.</p>
              </div>
            </div>

            <label className="flex items-start gap-3 text-sm text-gray-700">
              <input
                type="checkbox"
                name="accepts"
                checked={form.accepts}
                onChange={handleChange}
                required
                className="mt-1 h-4 w-4 text-primary-600 border-gray-300 rounded"
              />
              <span>
                I confirm that my entity is GST-registered and agree to the Terms and Privacy Policy.
              </span>
            </label>

            <button type="submit" className="btn-primary w-full">Create Account</button>
          </form>
          <p className="text-sm text-gray-600 mt-4 text-center">
            Already registered? <Link to="/auth/login" className="text-primary-700 font-semibold">Login</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
