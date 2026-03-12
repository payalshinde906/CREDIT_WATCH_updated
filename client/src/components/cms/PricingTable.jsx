
import React from 'react'

export default function PricingTable({ content }) {
    // content = { plans: [ { name, price, features: [] } ] }
    const plans = content?.plans || []

    return (
        <div className="py-12 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                    <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                        {content.title || "Our Offerings"}
                    </h2>
                    <p className="mt-4 text-xl text-gray-600">
                        {content.subtitle || "Choose the right plan for your business"}
                    </p>
                </div>
                <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-4">
                    {plans.map((plan) => (
                        <div key={plan.name} className="border border-gray-200 rounded-lg shadow-sm divide-y divide-gray-200 bg-white flex flex-col">
                            <div className="p-6">
                                <h3 className="text-lg leading-6 font-medium text-gray-900">{plan.name}</h3>
                                <p className="mt-4">
                                    <span className="text-4xl font-extrabold text-gray-900">{plan.price}</span>
                                    <span className="text-base font-medium text-gray-500">/mo</span>
                                </p>
                                <p className="mt-5 text-sm text-gray-500">{plan.description}</p>
                            </div>
                            <div className="pt-6 pb-8 px-6 flex-1 flex flex-col">
                                <ul className="space-y-4 flex-1">
                                    {plan.features?.map((feature) => (
                                        <li key={feature} className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                </svg>
                                            </div>
                                            <p className="ml-3 text-sm text-gray-700">{feature}</p>
                                        </li>
                                    ))}
                                </ul>
                                <div className="mt-8">
                                    <a
                                        href="/membership"
                                        className="block w-full bg-primary-600 border border-transparent rounded-md py-2 text-sm font-semibold text-white text-center hover:bg-primary-700"
                                    >
                                        Get started
                                    </a>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
