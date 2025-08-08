import React from 'react'

const StatsCard = ({ title, value }: { title: string; value: string }) => (
    <div className="bg-white p-4 rounded shadow">
        <h3 className="text-gray-500 text-sm">{title}</h3>
        <p className="text-2xl font-semibold">{value}</p>
    </div>
)

const DashboardPage = () => {
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold">歡迎回來，小安 👋</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard title="已上傳筆記" value="32" />
                <StatsCard title="上次提問" value="2025/08/07" />
                <StatsCard title="總提問次數" value="124" />
                <StatsCard title="剩餘 Token" value="42k" />
            </div>
        </div>
    )
}

export default DashboardPage
