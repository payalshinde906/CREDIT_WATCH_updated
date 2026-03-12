import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { cms } from '../../services/api/apiClient'

export default function CMSDashboard() {
    const [pages, setPages] = useState([])
    const [loading, setLoading] = useState(true)
    const [showCreate, setShowCreate] = useState(false)
    const [newPage, setNewPage] = useState({ title: '', slug: '' })

    const loadPages = async () => {
        setLoading(true)
        const res = await cms.listPages()
        if (res.ok && res.data) {
            setPages(res.data)
        }
        setLoading(false)
    }

    useEffect(() => {
        loadPages()
    }, [])

    const handleCreate = async (e) => {
        e.preventDefault()
        if (!newPage.title || !newPage.slug) return

        // Auto-format slug
        const formattedSlug = newPage.slug.toLowerCase().replace(/\s+/g, '-')

        const res = await cms.createPage({ ...newPage, slug: formattedSlug })
        if (res.ok) {
            setShowCreate(false)
            loadPages()
            setNewPage({ title: '', slug: '' })
        } else {
            alert("Failed to create page: " + (res.error || "Unknown error"))
        }
    }

    return (
        <section className="section-padding">
            <div className="container-custom space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-heading font-bold text-gray-900">CMS Admin</h1>
                    <button
                        onClick={() => setShowCreate(true)}
                        className="btn-primary"
                    >
                        + New Page
                    </button>
                </div>

                {showCreate && (
                    <div className="card bg-gray-50 border p-4 mb-4">
                        <h3 className="font-bold mb-3">Create New Page</h3>
                        <form onSubmit={handleCreate} className="flex gap-4 items-end">
                            <div className="flex-1">
                                <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Title</label>
                                <input
                                    className="w-full rounded border-gray-300 p-2"
                                    value={newPage.title}
                                    onChange={e => setNewPage({ ...newPage, title: e.target.value })}
                                    placeholder="e.g. Terms of Service"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Slug</label>
                                <input
                                    className="w-full rounded border-gray-300 p-2"
                                    value={newPage.slug}
                                    onChange={e => setNewPage({ ...newPage, slug: e.target.value })}
                                    placeholder="e.g. terms-of-service"
                                />
                            </div>
                            <div className="flex gap-2">
                                <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">Cancel</button>
                                <button type="submit" className="btn-primary">Create</button>
                            </div>
                        </form>
                    </div>
                )}

                <div className="card overflow-hidden p-0">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-100 text-gray-600 border-b">
                            <tr>
                                <th className="p-4">Title</th>
                                <th className="p-4">Slug</th>
                                <th className="p-4">Status</th>
                                <th className="p-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {loading ? (
                                <tr><td colSpan="4" className="p-4 text-center">Loading...</td></tr>
                            ) : pages.length === 0 ? (
                                <tr><td colSpan="4" className="p-4 text-center text-gray-500">No pages found.</td></tr>
                            ) : (
                                pages.map(page => (
                                    <tr key={page.id} className="hover:bg-gray-50">
                                        <td className="p-4 font-semibold">{page.title}</td>
                                        <td className="p-4 font-mono text-xs text-gray-600">/{page.slug}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${page.is_published ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                                {page.is_published ? 'LIVE' : 'DRAFT'}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right space-x-2">
                                            <a href={`/cms/${page.slug}`} target="_blank" className="text-gray-500 hover:text-primary-600 text-xs">Preview</a>
                                            <Link to={`/admin/cms/edit/${page.slug}`} className="btn-secondary py-1 px-3 text-xs">
                                                Edit
                                            </Link>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    )
}
