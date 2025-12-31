import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function AuthLanding() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-heading font-bold mb-3">Access CreditDataWatch</h1>
          <p className="text-gray-600">GST-validated access. Choose how you want to continue.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Link to="/auth/login" className="card text-center">
            <p className="font-heading font-semibold text-lg">Login</p>
            <p className="text-sm text-gray-600 mt-2">For registered GST entities</p>
          </Link>
          <Link to="/auth/register" className="card text-center">
            <p className="font-heading font-semibold text-lg">Register</p>
            <p className="text-sm text-gray-600 mt-2">Validate GST and start</p>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
