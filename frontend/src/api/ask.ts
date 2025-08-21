import { auth } from "../firebase";
import { BASE_URL } from "./conf";


export async function ask(query: string, timeoutMs = 100000): Promise<{ reply: string } | null> {
    if (!auth.currentUser) return null;


    const token = await auth.currentUser.getIdToken();

    const payload = {
        query
    };


    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    try {

        const res = await fetch(`${BASE_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
            signal: controller.signal,
        });

        if (!res.ok) {
            console.error("取得 LLM 回應失敗", await res.text())
            return null;
        }

        return await res.json();
    } catch (err: any) {
        if (err.name === "AbortError") {
            console.error(`Request 超時 (${timeoutMs} ms)`);
        } else {
            console.error("Fetch 發生錯誤:", err);
        }
        return null;
    } finally {
        clearTimeout(id);
    }
}
