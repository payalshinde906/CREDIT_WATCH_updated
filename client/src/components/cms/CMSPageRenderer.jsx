import React, { useEffect, useState } from 'react'
import { useParams, Navigate } from 'react-router-dom'
import { api } from '../../services/api/apiClient'

// Import static components to map
import HeroSection from '../home/HeroSection'
import StatsSection from '../home/StatsSection'
import ScamAlert from '../home/ScamAlert'
// We can create a generic ContentSection for flexible text/image blocks if needed
// For now, mapping existing ones.

// Mapping 'type' strings from DB to React Components
const SECTION_COMPONENTS = {
    hero: HeroSection,
    stats: StatsSection,
    scam_alert: ScamAlert,
    // 'custom_html': ({ content }) => <div dangerouslySetInnerHTML={{ __html: content.html }} />,
    // 'text_block': ({ content }) => <div className="container-custom py-10 prose">{content.text}</div> 
}

export default function CMSPageRenderer() {
    const { slug } = useParams()
    const [pageData, setPageData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        async function fetchPage() {
            setLoading(true)
            try {
                // Default to 'home' if no slug provided in route, or handle via route config
                const targetSlug = slug || 'home'
                const res = await api.get(`/cms/pages/${targetSlug}`)

                if (res.ok && res.data) {
                    setPageData(res.data)
                } else {
                    setError('Page not found')
                }
            } catch (err) {
                setError('Failed to load page')
            } finally {
                setLoading(false)
            }
        }
        fetchPage()
    }, [slug])

    if (loading) return <div className="flex h-screen items-center justify-center">Loading...</div>
    if (error) return <div className="container-custom py-20 text-center text-red-600">{error}</div>
    if (!pageData) return <Navigate to="/404" />

    // Render sections based on order_index
    const sortedSections = pageData.sections
        ?.filter(s => s.is_visible)
        ?.sort((a, b) => a.order_index - b.order_index) || []

    return (
        <main>
            {/* Optional: Render SEO Meta tags here using Helmet */}

            {sortedSections.map(section => {
                const Component = SECTION_COMPONENTS[section.type]
                if (!Component) {
                    return (
                        <div key={section.id} className="py-10 text-center text-gray-400 border-b">
                            [Section Type '{section.type}' Not Implemented]
                        </div>
                    )
                }
                // Pass flexible content props
                return <Component key={section.id} {...section.content} />
            })}

            {sortedSections.length === 0 && (
                <div className="container-custom py-20 text-center text-gray-500">
                    This page has no content yet.
                </div>
            )}
        </main>
    )
}
