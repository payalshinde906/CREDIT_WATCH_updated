import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { formatE164 } from '../../utils/phone'
import { isValidGstin } from '../../utils/validation'
import { useAuth } from '../../state/authContext'
import authService from '../../services/authService'

export default function Register() {
  const navigate = useNavigate()
  const { loadUser } = useAuth()
  const [form, setForm] = useState({
    company: '',
    email: '',
    password: '',
    confirm: '',
    phone: '',
    gstin: '',
    accepts: false,
  })
  const [otpCode, setOtpCode] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [sendingOtp, setSendingOtp] = useState(false)

  const [status, setStatus] = useState({ type: '', message: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm({ ...form, [e.target.name]: value })
  }

  const handleSendOtp = async () => {
    setStatus({ type: '', message: '' })
    
    // Validate email and phone first
    if (!form.email || !form.email.includes('@')) {
      setStatus({ type: 'error', message: 'Please enter a valid email address' })
      return
    }

    const phoneE164 = formatE164(form.phone)
    if (!phoneE164) {
      setStatus({ type: 'error', message: 'Enter a valid phone number with country code (e.g., +91XXXXXXXXXX)' })
      return
    }

    setSendingOtp(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: form.email.trim().toLowerCase(),
          phone: phoneE164,
        }),
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setOtpSent(true)
        setStatus({ 
          type: 'success', 
          message: data.message || 'OTP sent to your email and phone. Check your inbox/SMS.' 
        })
        // In dev mode, show OTP in console
        if (data.data?.otp_code) {
          console.log('OTP Code (dev):', data.data.otp_code)
          setStatus({ 
            type: 'success', 
            message: `OTP sent! Check console for OTP code: ${data.data.otp_code}` 
          })
        }
      } else {
        setStatus({ type: 'error', message: data.error?.message || data.message || 'Failed to send OTP' })
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Network error: ' + error.message })
    } finally {
      setSendingOtp(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus({ type: '', message: '' })

    // Validation
    if (!form.company || form.company.trim().length < 2) {
      setStatus({ type: 'error', message: 'Company name must be at least 2 characters' })
      return
    }

    if (!form.email || !form.email.includes('@') || !form.email.includes('.')) {
      setStatus({ type: 'error', message: 'Please enter a valid email address' })
      return
    }

    // Password validation - minimum 8 characters
    if (!form.password || form.password.trim().length < 8) {
      setStatus({ type: 'error', message: 'Password must be at least 8 characters' })
      return
    }

    // Password validation - maximum 64 characters
    if (form.password.trim().length > 64) {
      setStatus({ type: 'error', message: 'Password must be less than 64 characters' })
      return
    }

    if (form.password !== form.confirm) {
      setStatus({ type: 'error', message: 'Passwords do not match' })
      return
    }

    const phoneE164 = formatE164(form.phone)
    if (!phoneE164) {
      setStatus({ type: 'error', message: 'Enter a valid phone number with country code (e.g., +91XXXXXXXXXX)' })
      return
    }

    if (!isValidGstin(form.gstin)) {
      setStatus({ type: 'error', message: 'Enter a valid GSTIN (15 characters, format: 22AAAAA0000A1Z5)' })
      return
    }

    if (!form.accepts) {
      setStatus({ type: 'error', message: 'Please accept the terms and privacy policy' })
      return
    }

    if (!otpSent) {
      setStatus({ type: 'error', message: 'Please verify your email and phone by sending OTP first' })
      return
    }

    if (!otpCode || otpCode.length !== 6) {
      setStatus({ type: 'error', message: 'Please enter the 6-digit OTP code' })
      return
    }

    setSubmitting(true)
    try {
      const response = await authService.register({
        company_name: form.company.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password.trim(),
        phone: phoneE164,
        gstin: form.gstin.trim().toUpperCase(),
        otp_code: otpCode.trim(),
      })

      if (response.ok) {
        setStatus({ type: 'success', message: 'Account created successfully! Logging you in...' })
        await loadUser()
        setTimeout(() => navigate('/dashboard'), 1000)
      } else {
        setStatus({ type: 'error', message: response.error || 'Registration failed. Please check your information and try again.' })
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
                  minLength={8}
                  maxLength={64}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                />
                <p className="text-xs text-gray-500 mt-1">Minimum 8 characters, maximum 64</p>
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
                <div className="mt-2 flex gap-2">
                  <input
                    id="phone"
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    required
                    placeholder="+91XXXXXXXXXX"
                    disabled={otpSent}
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 disabled:bg-gray-100"
                  />
                  <button
                    type="button"
                    onClick={handleSendOtp}
                    disabled={sendingOtp || otpSent}
                    className="btn-secondary whitespace-nowrap disabled:opacity-50"
                  >
                    {sendingOtp ? 'Sending...' : otpSent ? 'Sent ✓' : 'Send OTP'}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">Include country code (e.g., +91 for India)</p>
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

            {/* OTP Verification */}
            {otpSent && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <label htmlFor="otp" className="text-sm font-semibold text-gray-700 block mb-2">
                  Enter OTP Code (sent to your email and phone)
                </label>
                <input
                  id="otp"
                  name="otp"
                  type="text"
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="000000"
                  className="w-full rounded-lg border border-blue-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 text-center text-2xl tracking-widest font-mono"
                  required
                />
                <p className="text-xs text-gray-600 mt-2">
                  Check your email inbox and SMS for the 6-digit OTP code
                </p>
              </div>
            )}

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