/**
 * ProtectedRoute Component
 * 
 * Wraps routes that require authentication
 * Redirects to login if user is not authenticated
 */

import { Navigate } from 'react-router-dom'
import { useAuth } from '../state/authContext'
import PropTypes from 'prop-types'

export default function ProtectedRoute({ children, requiredFeature = null }) {
  const { isAuthenticated, loading, canAccessFeature, user } = useAuth()

  // Still loading user state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />
  }

  // Check GSTIN is present (mandatory requirement)
  if (!user?.gstin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">GSTIN Required</h1>
          <p className="text-gray-600 mb-6">
            Your account must have a valid GSTIN to access this service.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            Please contact support to verify your GST registration.
          </p>
          <a href="/contact" className="btn-primary inline-block">
            Contact Support
          </a>
        </div>
      </div>
    )
  }

  // Check feature access if required
  if (requiredFeature && !canAccessFeature(requiredFeature)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🔒</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Access Restricted</h1>
          <p className="text-gray-600 mb-6">
            This feature is not available on your current plan.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            Contact support or upgrade your subscription to access {requiredFeature?.replaceAll('_', ' ').toLowerCase()}.
          </p>
          <a href="/membership" className="btn-primary inline-block">
            View Plans
          </a>
        </div>
      </div>
    )
  }

  return children
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  requiredFeature: PropTypes.string,
}
