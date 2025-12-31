import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '', gstin: '' })

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  const handleSubmit = (e) => {
    e.preventDefault()
    alert('Login submitted (stub). GST validation pending backend integration.')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 justify-center mb-3">
            <div className="h-10 w-10 rounded-xl bg-primary-600 text-white font-heading font-bold text-xl flex items-center justify-center">CD</div>
            <span className="font-heading font-bold text-2xl text-gray-900">CreditDataWatch</span>
          </Link>
          <h1 className="text-3xl font-heading font-bold">Login</h1>
          <p className="text-gray-600">GST-registered entities only</p>
        </div>
        <div className="card">
          <form className="space-y-4" onSubmit={handleSubmit}>
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
              <p className="text-xs text-gray-500 mt-1">GSTIN will be validated during login.</p>
            </div>
            <button type="submit" className="btn-primary w-full">Sign In</button>
          </form>
          <p className="text-sm text-gray-600 mt-4 text-center">
            New here? <Link to="/auth/register" className="text-primary-700 font-semibold">Create an account</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
