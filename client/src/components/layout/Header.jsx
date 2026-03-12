import { useState, useEffect } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../../state/authContext'
import { api } from '../../services/api/apiClient'

const navLinks = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'About', to: '/about' },
  { label: 'Services', to: '/services' },
  { label: 'Solutions', to: '/solutions' },
  { label: 'Membership', to: '/membership' },
  { label: 'Wallet', to: '/wallet' },
  { label: 'Offerings', to: '/offerings' },
  { label: 'Contact', to: '/contact' },
  { label: 'Credibility Index', to: '/credibility-index' },
]

export default function Header() {
  const [open, setOpen] = useState(false)
  const { user, isAuthenticated } = useAuth()
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    if (isAuthenticated && user) {
      loadProfile()
    }
  }, [isAuthenticated, user])

  // Refresh profile when window gains focus (user returns from another tab/page)
  useEffect(() => {
    const handleFocus = () => {
      if (isAuthenticated && user) {
        loadProfile()
      }
    }
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [isAuthenticated, user])

  // Listen for custom event to refresh profile (triggered from Account page after upload)
  useEffect(() => {
    const handleProfileUpdate = () => {
      if (isAuthenticated && user) {
        loadProfile()
      }
    }
    window.addEventListener('profileUpdated', handleProfileUpdate)
    return () => window.removeEventListener('profileUpdated', handleProfileUpdate)
  }, [isAuthenticated, user])

  const loadProfile = async () => {
    try {
      const response = await api.get('/account/profile')
      if (response.ok && response.data?.data) {
        setProfile(response.data.data)
      } else {
        // If profile doesn't exist, create an empty profile object
        setProfile(null)
      }
    } catch (err) {
      // Profile might not exist yet, that's okay
      setProfile(null)
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur shadow-sm">
      <div className="container-custom py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          {profile?.company_logo_url ? (
            <img 
              src={profile.company_logo_url} 
              alt="Logo" 
              className="h-10 w-10 rounded-xl object-cover shadow-md"
            />
          ) : (
            <div className="h-10 w-10 rounded-xl bg-primary-600 text-white font-heading font-bold text-xl flex items-center justify-center shadow-md">
              CD
            </div>
          )}
          <div className="flex flex-col leading-tight">
            <span className="font-heading font-bold text-lg">CreditDataWatch</span>
            <span className="text-xs text-gray-500">India's Credit Intelligence Hub</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `text-sm font-semibold transition-colors ${isActive ? 'text-primary-700' : 'text-gray-700 hover:text-primary-700'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          {isAuthenticated ? (
            <Link 
              to="/account" 
              className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary-50 border border-primary-200 hover:bg-primary-100 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-primary-600 text-white font-heading font-bold text-sm flex items-center justify-center overflow-hidden">
                {profile?.profile_photo_url ? (
                  <img src={profile.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
                ) : user?.company_name ? (
                  user.company_name.charAt(0).toUpperCase()
                ) : (
                  '👤'
                )}
              </div>
              <span className="text-sm font-semibold text-gray-900">
                {user?.company_name || user?.email || 'User'}
              </span>
            </Link>
          ) : (
            <>
              <Link to="/auth" className="text-sm font-semibold text-gray-700 hover:text-primary-700">
                Login / Register
              </Link>
              <Link to="/appointment" className="btn-accent text-sm shadow-lg">
                Book Appointment
              </Link>
            </>
          )}
        </nav>

        <button
          className="md:hidden p-2 rounded-lg border border-gray-200 text-gray-700"
          onClick={() => setOpen((prev) => !prev)}
          aria-label="Toggle menu"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {open ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden bg-white shadow-sm"
          >
            <div className="container-custom py-4 space-y-3">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `block text-base font-semibold ${isActive ? 'text-primary-700' : 'text-gray-700 hover:text-primary-700'
                    }`
                  }
                  onClick={() => setOpen(false)}
                >
                  {link.label}
                </NavLink>
              ))}
              {isAuthenticated ? (
                <Link
                  to="/account"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary-50 border border-primary-200"
                  onClick={() => setOpen(false)}
                >
                  <div className="w-8 h-8 rounded-full bg-primary-600 text-white font-heading font-bold text-sm flex items-center justify-center overflow-hidden">
                    {profile?.profile_photo_url ? (
                      <img src={profile.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
                    ) : user?.company_name ? (
                      user.company_name.charAt(0).toUpperCase()
                    ) : (
                      '👤'
                    )}
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    {user?.company_name || user?.email || 'User'}
                  </span>
                </Link>
              ) : (
                <>
                  <Link
                    to="/auth"
                    className="block text-base font-semibold text-gray-700 hover:text-primary-700"
                    onClick={() => setOpen(false)}
                  >
                    Login / Register
                  </Link>
                  <Link
                    to="/appointment"
                    className="btn-accent w-full text-center"
                    onClick={() => setOpen(false)}
                  >
                    Book Appointment
                  </Link>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
