import { useEffect, useState } from 'react'
import { useAuth } from '../../state/authContext'
import { api } from '../../services/api/apiClient'
import authService from '../../services/authService'
import { formatE164 } from '../../utils/phone'

export default function Account() {
  const { user, subscription, loadUser } = useAuth()
  const [form, setForm] = useState({ 
    company_name: '', 
    registered_name: '',
    email: '', 
    phone: '',
  })
  const [profile, setProfile] = useState(null)
  const [status, setStatus] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [otpStatus, setOtpStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [photoUploading, setPhotoUploading] = useState(false)
  const [logoUploading, setLogoUploading] = useState(false)

  // Load user and business profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        if (user) {
          setForm({
            company_name: user.company_name || '',
            registered_name: user.company_name || '',
            email: user.email || '',
            phone: user.phone || '',
          })
          
          // Fetch business profile
          const response = await api.get('/account/profile')
          if (response.ok && response.data?.data) {
            setProfile(response.data.data)
          }
        }
      } catch (err) {
        console.error('Error loading profile:', err)
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [user])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setStatus('')
    
    try {
      // Update business profile
      const response = await api.put('/account/profile', {
        company_name: form.company_name,
        registered_name: form.registered_name,
        email: form.email,
        phone: form.phone,
      })
      
      if (response.ok) {
        setStatus('Profile updated successfully')
        setProfile(response.data?.data)
        await loadUser()
      } else {
        setStatus('Failed to update profile')
      }
    } catch (err) {
      setStatus('Error updating profile: ' + err.message)
    }
  }

  const handleSendOtp = async () => {
    setOtpStatus('')
    const formatted = formatE164(form.phone)
    if (!formatted) {
      setOtpStatus('Enter a valid phone with country code')
      return
    }
    const res = await authService.sendPhoneChangeOtp(formatted)
    setOtpStatus(res.ok ? 'OTP sent to phone' : res.error || 'Failed to send OTP')
  }

  const handleVerifyOtp = async () => {
    setOtpStatus('')
    const formatted = formatE164(form.phone)
    const res = await authService.verifyPhoneChangeOtp(formatted, otpCode.trim())
    setOtpStatus(res.ok ? 'Phone verified and updated' : res.error || 'Invalid OTP')
    if (res.ok) {
      await loadUser()
    }
  }

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setPhotoUploading(true)
    try {
      // In a real app, upload to Google Drive and get URL
      // For now, simulate with a placeholder
      const driveUrl = `https://drive.google.com/file/d/photo-${Date.now()}/view`
      
      const response = await api.post('/account/profile-photo', {
        file_type: 'profile_photo',
        drive_url: driveUrl,
      })
      
      if (response.ok) {
        setProfile(prev => ({...prev, profile_photo_url: response.data?.data?.profile_photo_url}))
        setStatus('Profile photo updated')
      }
    } catch (err) {
      setStatus('Failed to upload photo: ' + err.message)
    } finally {
      setPhotoUploading(false)
    }
  }

  const handleLogoUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLogoUploading(true)
    try {
      // In a real app, upload to Google Drive and get URL
      const driveUrl = `https://drive.google.com/file/d/logo-${Date.now()}/view`
      
      const response = await api.post('/account/company-logo', {
        file_type: 'company_logo',
        drive_url: driveUrl,
      })
      
      if (response.ok) {
        setProfile(prev => ({...prev, company_logo_url: response.data?.data?.company_logo_url}))
        setStatus('Company logo updated')
      }
    } catch (err) {
      setStatus('Failed to upload logo: ' + err.message)
    } finally {
      setLogoUploading(false)
    }
  }

  const planLabel = subscription?.plan ? subscription.plan.toUpperCase() : 'BASE'
  const planStatus = subscription?.is_active ? 'Active' : 'Inactive'

  return (
    <div className="container-custom py-10 space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-heading font-bold text-gray-900">My Account</h1>
        <p className="text-gray-600">Manage your profile, uploads, plan, and secure phone changes with OTP.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* File Uploads Section */}
          <div className="card">
            <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Your Photos</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Profile Photo */}
              <div className="flex flex-col items-center gap-3">
                <div className="w-24 h-24 rounded-lg bg-gray-100 border-2 border-gray-200 flex items-center justify-center overflow-hidden">
                  {profile?.profile_photo_url ? (
                    <img src={profile.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-4xl">👤</span>
                  )}
                </div>
                <div className="w-full">
                  <label htmlFor="profile-photo" className="text-sm font-semibold text-gray-700 block mb-2">Profile Photo</label>
                  <input
                    id="profile-photo"
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    disabled={photoUploading}
                    className="w-full text-sm"
                  />
                  {photoUploading && <p className="text-xs text-gray-600 mt-1">Uploading...</p>}
                </div>
              </div>

              {/* Company Logo */}
              <div className="flex flex-col items-center gap-3">
                <div className="w-24 h-24 rounded-lg bg-gray-100 border-2 border-gray-200 flex items-center justify-center overflow-hidden">
                  {profile?.company_logo_url ? (
                    <img src={profile.company_logo_url} alt="Logo" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-4xl">🏢</span>
                  )}
                </div>
                <div className="w-full">
                  <label htmlFor="company-logo" className="text-sm font-semibold text-gray-700 block mb-2">Company Logo</label>
                  <input
                    id="company-logo"
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    disabled={logoUploading}
                    className="w-full text-sm"
                  />
                  {logoUploading && <p className="text-xs text-gray-600 mt-1">Uploading...</p>}
                </div>
              </div>
            </div>
          </div>

          {/* Profile Information */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-heading font-semibold text-gray-900">Profile Information</h2>
              {loading && <p className="text-sm text-gray-500">Loading...</p>}
            </div>
            {status && <div className={`text-sm mb-3 p-3 rounded-lg ${status.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{status}</div>}
            <form className="space-y-4" onSubmit={handleSave}>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold text-gray-700" htmlFor="company_name">Company Name</label>
                  <input
                    id="company_name"
                    name="company_name"
                    value={form.company_name}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-700" htmlFor="registered_name">Registered Legal Name</label>
                  <input
                    id="registered_name"
                    name="registered_name"
                    value={form.registered_name}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold text-gray-700" htmlFor="email">Work Email</label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-700" htmlFor="gstin">GSTIN</label>
                  <input
                    id="gstin"
                    value={user?.gstin || ''}
                    disabled
                    className="mt-2 w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-gray-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-700 flex items-center justify-between" htmlFor="phone">
                  <span>Phone</span>
                  <span className="text-xs text-gray-500">OTP required to confirm change</span>
                </label>
                <div className="mt-2 flex gap-2">
                  <input
                    id="phone"
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
                    required
                  />
                  <button type="button" onClick={handleSendOtp} className="btn-secondary text-sm whitespace-nowrap">Send OTP</button>
                </div>
                <div className="mt-3 flex gap-2 items-center">
                  <input
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    placeholder="Enter OTP"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                  />
                  <button type="button" onClick={handleVerifyOtp} className="btn-primary text-sm whitespace-nowrap">Verify</button>
                </div>
                {otpStatus && <p className="text-xs text-gray-600 mt-2">{otpStatus}</p>}
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button type="submit" className="btn-primary">Save Changes</button>
                <a href="/membership" className="btn-secondary">Manage Plan</a>
              </div>
            </form>
          </div>
        </div>

        {/* Plan & Access Sidebar */}
        <div className="card space-y-3">
          <h2 className="text-xl font-heading font-semibold text-gray-900">Plan & Access</h2>
          <div className="rounded-lg border border-gray-200 px-4 py-3">
            <p className="text-sm text-gray-500">Current Plan</p>
            <p className="text-lg font-heading font-semibold text-gray-900">{planLabel}</p>
            <p className="text-sm text-green-700">Status: {planStatus}</p>
            <p className="text-sm text-gray-500">Expiry: {subscription?.expiry_date?.slice(0, 10) || '—'}</p>
          </div>
          <p className="text-sm text-gray-700">Need a higher plan for advanced features? Upgrade in Membership.</p>
          <a href="/membership" className="btn-primary w-full text-center">View Plans</a>
        </div>
      </div>
    </div>
  )
}
