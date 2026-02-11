import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { isValidGstin } from '../../utils/validation'
import { useAuth } from '../../state/authContext'
import authService from '../../services/authService'

export default function Login() {
  const navigate = useNavigate()
  const { login, loadUser } = useAuth()
  const [form, setForm] = useState({ email: '', password: '', gstin: '' })
  const [status, setStatus] = useState({ type: '', message: '' })
  const [submitting, setSubmitting] = useState(false)
  const [mode, setMode] = useState('password')
  const [otpEmail, setOtpEmail] = useState('')
  const [otpGstin, setOtpGstin] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [sendingOtp, setSendingOtp] = useState(false)
  const [submittingOtp, setSubmittingOtp] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus({ type: '', message: '' })
    
    // Validation
    if (!form.email || !form.email.includes('@')) {
      setStatus({ type: 'error', message: 'Please enter a valid email address' })
      return
    }
    
    if (!isValidGstin(form.gstin)) {
      setStatus({ type: 'error', message: 'Enter a valid GSTIN (15 characters)' })
      return
    }
    
    if (!form.password || form.password.length < 6) {
      setStatus({ type: 'error', message: 'Password must be at least 6 characters' })
      return
    }
    
    setSubmitting(true)
    try {
      const success = await login({
        email: form.email.trim().toLowerCase(),
        password: form.password,
        gstin: form.gstin.trim().toUpperCase(),
      })
      
      if (success) {
        setStatus({ type: 'success', message: 'Login successful! Redirecting...' })
        // Redirect to dashboard after short delay
        setTimeout(() => navigate('/dashboard'), 500)
      } else {
        setStatus({ type: 'error', message: 'Invalid email, password, or GSTIN. Please check your credentials.' })
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Network error: ' + error.message })
    } finally {
      setSubmitting(false)
    }
  }

  const handleSendEmailLoginOtp = async () => {
    setStatus({ type: '', message: '' })
    if (!otpEmail || !otpEmail.includes('@')) {
      setStatus({ type: 'error', message: 'Enter a valid email address' })
      return
    }
    if (!isValidGstin(otpGstin)) {
      setStatus({ type: 'error', message: 'Enter a valid GSTIN (15 characters)' })
      return
    }
    setSendingOtp(true)
    const res = await authService.sendEmailLoginOtp(otpEmail.trim().toLowerCase())
    if (res.ok) {
      setOtpSent(true)
      setStatus({ type: 'success', message: 'OTP sent to your email' })
    } else {
      setStatus({ type: 'error', message: res.error || 'Failed to send OTP' })
    }
    setSendingOtp(false)
  }

  const handleVerifyEmailLoginOtp = async () => {
    setStatus({ type: '', message: '' })
    if (!otpCode || otpCode.length !== 6) {
      setStatus({ type: 'error', message: 'Enter the 6-digit OTP code' })
      return
    }
    setSubmittingOtp(true)
    const res = await authService.verifyEmailLoginOtp(
      otpEmail.trim().toLowerCase(),
      otpGstin.trim().toUpperCase(),
      otpCode.trim()
    )
    if (res.ok) {
      await loadUser()
      setStatus({ type: 'success', message: 'Login successful! Redirecting...' })
      setTimeout(() => navigate('/dashboard'), 500)
    } else {
      setStatus({ type: 'error', message: res.error || 'Invalid OTP' })
    }
    setSubmittingOtp(false)
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
          {status.message && (
            <div className={`mb-4 rounded-lg px-4 py-3 text-sm font-semibold ${
              status.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
            }`}>
              {status.message}
            </div>
          )}
          <div className="flex gap-2 mb-4">
            <button
              className={`btn-secondary ${mode === 'password' ? 'bg-primary-600 text-white' : ''}`}
              onClick={() => setMode('password')}
              type="button"
            >
              Password Login
            </button>
            <button
              className={`btn-secondary ${mode === 'otp' ? 'bg-primary-600 text-white' : ''}`}
              onClick={() => setMode('otp')}
              type="button"
            >
              Email OTP Login
            </button>
          </div>
          {mode === 'password' ? (
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
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Remember me
                </label>
              </div>
              <Link to="/auth/forgot-password" className="text-sm text-primary-600 hover:text-primary-700 font-semibold">
                Forgot password?
              </Link>
            </div>
            <button type="submit" className="btn-primary w-full disabled:opacity-60" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-700">Work Email</label>
                <input
                  type="email"
                  value={otpEmail}
                  onChange={(e) => setOtpEmail(e.target.value)}
                  disabled={otpSent}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 disabled:bg-gray-100"
                />
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-700">GSTIN (mandatory)</label>
                <input
                  value={otpGstin}
                  onChange={(e) => setOtpGstin(e.target.value)}
                  disabled={otpSent}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 disabled:bg-gray-100"
                  placeholder="22AAAAA0000A1Z5"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleSendEmailLoginOtp}
                  disabled={sendingOtp || otpSent}
                  className="btn-secondary whitespace-nowrap disabled:opacity-50"
                >
                  {sendingOtp ? 'Sending...' : otpSent ? 'Sent ✓' : 'Send OTP'}
                </button>
              </div>
              {otpSent && (
                <div>
                  <label className="text-sm font-semibold text-gray-700">Enter OTP</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      maxLength={6}
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                      placeholder="000000"
                      className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-center text-xl tracking-widest font-mono focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    />
                    <button
                      type="button"
                      onClick={handleVerifyEmailLoginOtp}
                      className="btn-primary whitespace-nowrap disabled:opacity-50"
                      disabled={submittingOtp}
                    >
                      {submittingOtp ? 'Verifying...' : 'Verify & Login'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
          <p className="text-sm text-gray-600 mt-4 text-center">
            New here? <Link to="/auth/register" className="text-primary-700 font-semibold">Create an account</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
