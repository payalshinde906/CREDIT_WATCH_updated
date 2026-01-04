import { Routes, Route } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import Home from '../pages/Home'
import About from '../pages/About'
import Services from '../pages/Services'
import Solutions from '../pages/Solutions'
import Offerings from '../pages/Offerings'
import Contact from '../pages/Contact'
import Appointment from '../pages/Appointment'
import NotFound from '../pages/NotFound'

import ReportOverdue from '../pages/services/ReportOverdue'
import CreditManagement from '../pages/services/CreditManagement'
import PartnersReport from '../pages/services/PartnersReport'
import Finalization from '../pages/services/Finalization'

import B2B from '../pages/solutions/B2B'
import MSME from '../pages/solutions/MSME'
import BusinessCredit from '../pages/solutions/BusinessCredit'
import BusinessDebt from '../pages/solutions/BusinessDebt'

import AuthLanding from '../pages/auth/AuthLanding'
import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'
import ForgotPassword from '../pages/auth/ForgotPassword'
import Dashboard from '../pages/Dashboard'
import Membership from '../pages/Membership'
import PurchaseOrders from '../pages/PurchaseOrders'
import Invoices from '../pages/Invoices'
import Defaulters from '../pages/Defaulters'
import CreditReports from '../pages/CreditReports'
import Settlement from '../pages/Settlement'
import Privacy from '../pages/Privacy'
import Terms from '../pages/Terms'
import Account from '../pages/account/Account'
import ProtectedRoute from '../components/ProtectedRoute'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="services" element={<Services />} />
        <Route path="services/report-overdue" element={<ReportOverdue />} />
        <Route path="services/credit-management" element={<CreditManagement />} />
        <Route path="services/partners-report" element={<PartnersReport />} />
        <Route path="services/finalization" element={<Finalization />} />

        <Route path="solutions" element={<Solutions />} />
        <Route path="solutions/b2b" element={<B2B />} />
        <Route path="solutions/msme" element={<MSME />} />
        <Route path="solutions/business-credit" element={<BusinessCredit />} />
        <Route path="solutions/business-debt" element={<BusinessDebt />} />

        <Route path="offerings" element={<Offerings />} />
        <Route path="contact" element={<Contact />} />
        <Route path="appointment" element={<Appointment />} />
        <Route
          path="account"
          element={(
            <ProtectedRoute>
              <Account />
            </ProtectedRoute>
          )}
        />
        <Route
          path="dashboard"
          element={(
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          )}
        />
        <Route path="membership" element={<Membership />} />
        <Route
          path="purchase-orders"
          element={(
            <ProtectedRoute requiredFeature="PO_MANAGEMENT">
              <PurchaseOrders />
            </ProtectedRoute>
          )}
        />
        <Route
          path="invoices"
          element={(
            <ProtectedRoute requiredFeature="CREDIT_MANAGEMENT">
              <Invoices />
            </ProtectedRoute>
          )}
        />
        <Route
          path="defaulters"
          element={(
            <ProtectedRoute requiredFeature="REPORT_OVERDUE">
              <Defaulters />
            </ProtectedRoute>
          )}
        />
        <Route
          path="credit-reports"
          element={(
            <ProtectedRoute requiredFeature="CREDIT_REPORTS">
              <CreditReports />
            </ProtectedRoute>
          )}
        />
        <Route
          path="settlement"
          element={(
            <ProtectedRoute requiredFeature="SETTLEMENT">
              <Settlement />
            </ProtectedRoute>
          )}
        />
        <Route path="privacy" element={<Privacy />} />
        <Route path="terms" element={<Terms />} />

        <Route path="*" element={<NotFound />} />
      </Route>

      <Route path="auth" element={<AuthLanding />} />
      <Route path="auth/login" element={<Login />} />
      <Route path="auth/register" element={<Register />} />
      <Route path="auth/forgot-password" element={<ForgotPassword />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
