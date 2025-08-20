import { auth } from "../firebase";
import { BASE_URL } from "./conf";


export type DashboardStats = {
    uploaded_papers: number;
    last_query_date: string;
    total_queries: number;
    remaining_tokens: number;
};

export async function fetchDashboardStats(timeoutMs = 10000): Promise<DashboardStats | null> {
    if (!auth.currentUser) return null;

    const token = await auth.currentUser.getIdToken();
    console.log(`${BASE_URL}/dashboard/stats`);


    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(`${BASE_URL}/dashboard/stats`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
            signal: controller.signal,
        });

        if (!res.ok) {
            console.error("取得 Dashboard 統計失敗", await res.text());
            return null;
        }

        const data = await res.json();
        return data as DashboardStats;
    } catch (err: any) {
        if (err.name === "AbortError") {
            console.error(`Dashboard 統計請求超時 (${timeoutMs} ms)`);
        } else {
            console.error("Fetch 發生錯誤:", err);
        }
        return null;
    } finally {
        clearTimeout(id);
    }
}
