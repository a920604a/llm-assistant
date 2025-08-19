import { auth } from "../firebase";
import { BASE_URL } from "./conf";


export type DashboardStats = {
    uploaded_papers: number;
    last_query_date: string;
    total_queries: number;
    remaining_tokens: number;
};

export async function fetchDashboardStats(): Promise<DashboardStats | null> {
    if (!auth.currentUser) return null;

    const token = await auth.currentUser.getIdToken();

    const res = await fetch(`${BASE_URL}/dashboard/stats`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        console.error("取得 Dashboard 統計失敗", await res.text());
        return null;
    }

    const data = await res.json();
    return data as DashboardStats;
}
