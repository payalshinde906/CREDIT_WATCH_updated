import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const navLinks = [
  { label: 'About', to: '/about' },
  { label: 'Services', to: '/services' },
  { label: 'Solutions', to: '/solutions' },
  { label: 'Offerings', to: '/offerings' },
  { label: 'Contact', to: '/contact' },
]

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur shadow-sm">
      <div className="container-custom py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary-600 text-white font-heading font-bold text-xl flex items-center justify-center shadow-md">
            CD
          </div>
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
                `text-sm font-semibold transition-colors ${
                  isActive ? 'text-primary-700' : 'text-gray-700 hover:text-primary-700'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <Link to="/auth" className="text-sm font-semibold text-gray-700 hover:text-primary-700">
            Login / Register
          </Link>
          <Link to="/appointment" className="btn-accent text-sm shadow-lg">
            Book Appointment
          </Link>
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
                    `block text-base font-semibold ${
                      isActive ? 'text-primary-700' : 'text-gray-700 hover:text-primary-700'
                    }`
                  }
                  onClick={() => setOpen(false)}
                >
                  {link.label}
                </NavLink>
              ))}
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
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
