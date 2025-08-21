import { useEffect, useState } from "react";
import { fetchDashboardStats, type DashboardStats } from "../api/dashboard";


const StatsCard = ({ title, value }: { title: string; value: string }) => (
    <div className="bg-white p-4 rounded shadow">
        <h3 className="text-gray-500 text-sm">{title}</h3>
        <p className="text-2xl font-semibold">{value}</p>
    </div>
);

const DashboardPage = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);

    useEffect(() => {
        fetchDashboardStats().then((data) => {
            if (data) setStats(data);
        });
    }, []);

    if (!stats) {
        return <div>載入中...</div>;
    }

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold">歡迎回來，小安 👋</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard title="論文筆數" value={stats.uploaded_papers.toString()} />
                <StatsCard title="上次提問" value={stats.last_query_date} />
                <StatsCard title="總提問次數" value={stats.total_queries.toString()} />
                <StatsCard title="剩餘 Token" value={stats.remaining_tokens.toString()} />
            </div>
        </div>
    );
};

export default DashboardPage;
