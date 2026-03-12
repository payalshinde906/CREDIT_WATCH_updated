import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { cms } from '../../services/api/apiClient'

const PREDEFINED_SECTIONS = [
    { type: 'hero', name: 'Hero Banner' },
    { type: 'stats', name: 'Stats Counter' },
    { type: 'scam_alert', name: 'Scam Alert' },
    { type: 'text_block', name: 'Text Block' }
]

export default function CMSPageEditor() {
    const { slug } = useParams()
    const [page, setPage] = useState(null)
    const [loading, setLoading] = useState(true)
    const [addingSection, setAddingSection] = useState(false)

    const loadPage = useCallback(async () => {
        setLoading(true)
        const res = await cms.getPage(slug)
        if (res.ok && res.data) {
            // Sort sections
            res.data.sections.sort((a, b) => a.order_index - b.order_index)
            setPage(res.data)
        }
        setLoading(false)
    }, [slug])

    useEffect(() => {
        loadPage()
    }, [loadPage])

    const handleAddSection = async (type) => {
        if (!page) return
        const newOrder = page.sections.length > 0 ? Math.max(...page.sections.map(s => s.order_index)) + 1 : 0
        const res = await cms.addSection(page.id, {
            type,
            order_index: newOrder,
            is_visible: true,
            content: {} // Empty content initially
        })

        if (res.ok) {
            setAddingSection(false)
            loadPage()
        }
    }

    const handleDeleteSection = async (id) => {
        if (!confirm("Delete this section?")) return
        await cms.deleteSection(id)
        loadPage()
    }

    const handleMove = async (index, direction) => {
        // Simple swap logic for UI, backend update needed
        // Ideally, reorder whole list and send bulk update
        if (!page) return
        const sections = [...page.sections]
        const targetIndex = index + direction

        if (targetIndex < 0 || targetIndex >= sections.length) return

        // Swap order_index
        const temp = sections[index].order_index
        sections[index].order_index = sections[targetIndex].order_index
        sections[targetIndex].order_index = temp

        // Swap in array
        const tempItem = sections[index]
        sections[index] = sections[targetIndex]
        sections[targetIndex] = tempItem

        setPage({ ...page, sections }) // Optimistic update

        // Send bulk update
        const payload = sections.map(s => ({ id: s.id, order_index: s.order_index }))
        await cms.reorderSections(page.id, payload)
    }

    if (loading) return <div>Loading...</div>
    if (!page) return <div>Page not found</div>

    return (
        <div className="min-h-screen bg-gray-100 pb-20">
            <header className="bg-white border-b sticky top-0 z-10">
                <div className="container-custom py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/admin/cms" className="text-gray-500 hover:text-gray-900">← Back</Link>
                        <h1 className="text-xl font-bold">{page.title}</h1>
                        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">/{page.slug}</span>
                    </div>
                    <div className="flex gap-2">
                        <a href={`/cms/${page.slug}`} target="_blank" className="btn-secondary text-sm">View Page</a>
                        <button onClick={() => setAddingSection(true)} className="btn-primary text-sm">+ Add Section</button>
                    </div>
                </div>
            </header>

            <div className="container-custom py-8 max-w-4xl">

                {addingSection && (
                    <div className="bg-white p-4 rounded shadow mb-6 border border-primary-200">
                        <h3 className="font-bold mb-3">Choose Section Type</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {PREDEFINED_SECTIONS.map(s => (
                                <button
                                    key={s.type}
                                    onClick={() => handleAddSection(s.type)}
                                    className="p-3 border rounded hover:bg-primary-50 hover:border-primary-300 text-left transition-colors"
                                >
                                    <span className="font-semibold block">{s.name}</span>
                                    <span className="text-xs text-gray-500">{s.type}</span>
                                </button>
                            ))}
                        </div>
                        <button onClick={() => setAddingSection(false)} className="mt-3 text-sm text-gray-500 hover:underline">Cancel</button>
                    </div>
                )}

                {page.sections.length === 0 ? (
                    <div className="text-center py-20 text-gray-400 bg-white rounded border border-dashed">
                        No sections yet. Add one to start building.
                    </div>
                ) : (
                    <div className="space-y-4">
                        {page.sections.map((section, idx) => (
                            <div key={section.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                <div className="bg-gray-50 p-3 flex items-center justify-between border-b cursor-move">
                                    <div className="flex items-center gap-3">
                                        <span className="text-gray-400 font-mono text-xs">#{idx + 1}</span>
                                        <span className="font-semibold text-gray-700 capitalize">{section.type.replace('_', ' ')}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => handleMove(idx, -1)}
                                            disabled={idx === 0}
                                            className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
                                        >
                                            ⬆️
                                        </button>
                                        <button
                                            onClick={() => handleMove(idx, 1)}
                                            disabled={idx === page.sections.length - 1}
                                            className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
                                        >
                                            ⬇️
                                        </button>
                                        <div className="w-px h-4 bg-gray-300 mx-1"></div>
                                        <button
                                            onClick={() => handleDeleteSection(section.id)}
                                            className="text-red-500 text-xs font-bold hover:underline"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                </div>
                                <div className="p-4">
                                    {/* Editor Form Placeholder */}
                                    <p className="text-sm text-gray-500 mb-2">Content Configuration (JSON)</p>
                                    <textarea
                                        className="w-full text-xs font-mono bg-gray-50 border rounded p-2 h-24"
                                        disabled
                                        value={JSON.stringify(section.content, null, 2)}
                                    />
                                    <p className="text-xs text-amber-600 mt-2">
                                        * Full visual editor coming in Phase 2. For now, content is managed via generic JSON.
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
