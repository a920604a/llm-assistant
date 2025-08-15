import { auth } from "../firebase";
import { BASE_URL } from "./conf";

const DEV_BASE_URL = "http://localhost:8022/api"

export async function ask(query: string): Promise<{ reply: string } | null> {
    if (!auth.currentUser) return null;

    const token = await auth.currentUser.getIdToken();

    const res = await fetch(`${BASE_URL}/ask`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query }),
    });

    if (!res.ok) {
        console.error("取得 LLM 回應失敗", await res.text())
        return null;
    }

    return await res.json();
}
