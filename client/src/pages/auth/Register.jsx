import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { formatE164 } from '../../utils/phone'
import { isValidGstin } from '../../utils/validation'
import authService from '../../services/authService'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    company: '',
    email: '',
    password: '',
    confirm: '',
    phone: '',
    gstin: '',
    accepts: false,
  })

  const [status, setStatus] = useState({ type: '', message: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm({ ...form, [e.target.name]: value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus({ type: '', message: '' })

    if (form.password !== form.confirm) {
      setStatus({ type: 'error', message: 'Passwords do not match' })
      return
    }

    const phoneE164 = formatE164(form.phone)
    if (!phoneE164) {
      setStatus({ type: 'error', message: 'Enter a valid phone with country code' })
      return
    }

    if (!isValidGstin(form.gstin)) {
      setStatus({ type: 'error', message: 'Enter a valid GSTIN' })
      return
    }

    if (!form.accepts) {
      setStatus({ type: 'error', message: 'Please accept the terms and privacy policy' })
      return
    }

    setSubmitting(true)
    try {
      const response = await authService.register({
        company_name: form.company,
        email: form.email,
        password: form.password,
        phone: phoneE164,
        gstin: form.gstin,
      })

      if (response.ok) {
        setStatus({ type: 'success', message: 'Account created! Redirecting to login...' })
        // Redirect to login after short delay
        setTimeout(() => navigate('/auth/login'), 1500)
      } else {
        setStatus({ type: 'error', message: response.error || 'Registration failed' })
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Network error: ' + error.message })
    } finally {
      setSubmitting(false)
    }
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
          <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            <p className="font-semibold">📌 Important:</p>
            <p>Registration creates your account. You'll then choose a subscription plan to unlock features.</p>
          </div>
        </div>
        <div className="card">
          {status.message && (
            <div className={`mb-4 rounded-lg px-4 py-3 text-sm font-semibold ${status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
              }`}>
              {status.message}
            </div>
          )}
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
              <span className="text-gray-700">
                I confirm that my entity is GST-registered and agree to the{' '}
                <Link to="/terms" target="_blank" className="text-primary-600 hover:text-primary-700 underline font-medium">Terms</Link>
                {' '}and{' '}
                <Link to="/privacy" target="_blank" className="text-primary-600 hover:text-primary-700 underline font-medium">Privacy Policy</Link>.
              </span>
            </label>

            <button
              type="submit"
              className="btn-primary w-full disabled:opacity-60"
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Create Account'}
            </button>
          </form>
          <p className="text-sm text-gray-600 mt-4 text-center">
            Already registered? <Link to="/auth/login" className="text-primary-700 font-semibold">Login</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
