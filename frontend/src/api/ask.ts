import { auth } from "../firebase";
import { BASE_URL } from "./conf";


export async function ask(
    query: string,
    mode: "standard" | "stream" = "standard",
    onStreamChunk?: (chunk: string) => void
): Promise<{ reply: string } | null> {

    if (!auth.currentUser) return null;


    const token = await auth.currentUser.getIdToken();

    const payload = {
        query
    };

    // 根據模式給不同的預設 timeout
    const finalTimeout = (mode === "stream" ? 100000 : 60000);


    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), finalTimeout);

    try {
        const endpoint = mode === "standard" ? `${BASE_URL}/v1/ask` : `${BASE_URL}/v1/stream`
        console.log("Calling endpoint:", endpoint);

        const res = await fetch(endpoint, {
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

        // ✅ Streaming 模式
        if (mode === "stream" && res.body) {
            const reader = res.body.getReader()
            const decoder = new TextDecoder()
            let fullReply = ""

            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                const chunk = decoder.decode(value, { stream: true })

                fullReply += chunk
                onStreamChunk?.(chunk) // 動態更新前端
            }
            return { reply: fullReply }
        }

        // ✅ Standard 模式
        const data = await res.json()  // ✅ 只讀一次
        console.log("LLM 回覆", data)
        // 在標準模式也呼叫 callback 以統一更新邏輯
        if (onStreamChunk) {
            onStreamChunk(data);
        }
        return { reply: data }

    } catch (err: any) {
        if (err.name === "AbortError") {
            console.error(`Request 超時 (${finalTimeout} ms)`);
        } else {
            console.error("Fetch 發生錯誤:", err);
        }
        return null;
    } finally {
        clearTimeout(id);
    }
}
