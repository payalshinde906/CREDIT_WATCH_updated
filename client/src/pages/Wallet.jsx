import { useEffect, useState } from 'react'
import { wallet } from '../services/api/apiClient'
import { useAuth } from '../state/authContext'

export default function Wallet() {
    const { user } = useAuth()
    const [balance, setBalance] = useState(0)
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)
    const [redeemAmount, setRedeemAmount] = useState('')
    const [msg, setMsg] = useState('')

    useEffect(() => {
        fetchWalletData()
    }, [])

    const fetchWalletData = async () => {
        setLoading(true)
        try {
            // Parallel fetch balance and history
            const [balRes, histRes] = await Promise.all([
                wallet.getBalance(),
                wallet.getHistory()
            ])

            if (balRes.ok) setBalance(balRes.data?.balance || 0)
            if (histRes.ok) setHistory(histRes.data?.items || [])

        } catch (error) {
            console.error('Wallet fetch error:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRedeem = async (e) => {
        e.preventDefault()
        if (!redeemAmount || isNaN(redeemAmount) || Number(redeemAmount) <= 0) {
            setMsg('Enter a valid amount')
            return
        }
        if (Number(redeemAmount) > balance) {
            setMsg('Insufficient balance')
            return
        }

        const res = await wallet.redeem(Number(redeemAmount), 'SUBSCRIPTION_DISCOUNT')
        if (res.ok) {
            setMsg(`Success! Redeemed ${redeemAmount} points.`)
            setRedeemAmount('')
            fetchWalletData() // Refresh
        } else {
            setMsg(res.error || 'Redemption failed')
        }
    }

    return (
        <section className="section-padding">
            <div className="container-custom space-y-8">

                {/* Header */}
                <div className="space-y-2">
                    <p className="text-sm text-gray-500">Rewards & Credits</p>
                    <h1 className="text-3xl font-heading font-bold text-gray-900">My Wallet</h1>
                    <p className="text-gray-600">Track your cashback points and referral earnings.</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-6">

                    {/* Balance Card */}
                    <div className="card bg-gradient-to-br from-primary-600 to-primary-800 text-white shadow-xl">
                        <p className="text-primary-100 font-medium mb-2">Available Balance</p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-5xl font-bold">{loading ? '...' : balance}</span>
                            <span className="text-primary-200">pts</span>
                        </div>
                        <p className="text-xs text-primary-200 mt-4 opacity-80">
                            1 Point = ₹1 (Applicable on Subscription renewals)
                        </p>
                    </div>

                    {/* Redeem Action */}
                    <div className="card lg:col-span-2">
                        <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Redeem Points</h2>
                        <form onSubmit={handleRedeem} className="flex gap-4 items-end">
                            <div className="flex-1 space-y-1">
                                <label className="text-sm font-medium text-gray-700">Amount to redeem</label>
                                <input
                                    type="number"
                                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-primary-200 focus:border-primary-500"
                                    placeholder="Enter points"
                                    value={redeemAmount}
                                    onChange={(e) => setRedeemAmount(e.target.value)}
                                />
                            </div>
                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={loading || balance === 0}
                            >
                                Apply to Subscription
                            </button>
                        </form>
                        {msg && <p className={`text-sm mt-3 ${msg.includes('Success') ? 'text-green-600' : 'text-red-500'}`}>{msg}</p>}

                        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-100">
                            <h3 className="text-sm font-bold text-gray-900 mb-2">How to earn?</h3>
                            <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                                <li>Report a defaulter successfully: <span className="font-medium text-gray-800">50 pts</span></li>
                                <li>Refer a business: <span className="font-medium text-gray-800">100 pts</span></li>
                                <li>Renew subscription early: <span className="font-medium text-gray-800">5% Cashback</span></li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* History Table */}
                <div className="card">
                    <h2 className="text-xl font-heading font-semibold text-gray-900 mb-4">Transaction History</h2>
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                            <thead>
                                <tr className="text-left text-gray-500 border-b border-gray-100">
                                    <th className="pb-3 pl-2">Date</th>
                                    <th className="pb-3">Description</th>
                                    <th className="pb-3">Type</th>
                                    <th className="pb-3 text-right pr-4">Amount</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {loading && <tr><td colSpan="4" className="py-4 text-center text-gray-400">Loading...</td></tr>}
                                {!loading && history.length === 0 && (
                                    <tr><td colSpan="4" className="py-8 text-center text-gray-400">No transactions found</td></tr>
                                )}
                                {history.map((tx) => (
                                    <tr key={tx.id} className="text-gray-700">
                                        <td className="py-3 pl-2">{new Date(tx.created_at).toLocaleDateString()}</td>
                                        <td className="py-3 font-medium">{tx.reference_type || 'Transaction'}</td>
                                        <td className="py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${tx.trans_type === 'CREDIT' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                                {tx.trans_type}
                                            </span>
                                        </td>
                                        <td className={`py-3 text-right pr-4 font-bold ${tx.trans_type === 'CREDIT' ? 'text-green-600' : 'text-gray-900'}`}>
                                            {tx.trans_type === 'CREDIT' ? '+' : '-'}{tx.amount}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </section>
    )
}
