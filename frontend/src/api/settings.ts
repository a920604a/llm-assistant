// src/utils/settings.ts
import { auth } from "../firebase";
import { BASE_URL } from "./conf";



export interface SystemSettings {
    user_language: string;      // ex: "en", "zh"
    translate: boolean;         // 是否啟用自動翻譯
    system_prompt: string;      // LLM 系統提示
    top_k: number;              // 檢索 top K
    use_rag: boolean;           // 是否啟用 RAG
    subscribe_email: boolean;   // 是否訂閱每日 Email
    reranker_enabled: boolean;  // 是否啟用 reranker
    temperature: number;        // LLM 溫度
}

export const DEFAULT_SETTINGS: SystemSettings = {
    user_language: "English",
    translate: false,
    system_prompt: "",
    top_k: 5,
    use_rag: true,
    subscribe_email: false,
    reranker_enabled: true,
    temperature: 0.6,
};


// 包裝 fetch + timeout
async function fetchWithTimeout(url: string, options: RequestInit, timeoutMs: number) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
        return await fetch(url, { ...options, signal: controller.signal });
    } finally {
        clearTimeout(id);
    }
}

// 取得使用者設定
export async function getSystemSettings(timeoutMs = 10000): Promise<SystemSettings> {
    if (!auth.currentUser) return DEFAULT_SETTINGS;

    const token = await auth.currentUser.getIdToken();
    console.log(`${BASE_URL}/user/settings`);

    try {
        const res = await fetchWithTimeout(`${BASE_URL}/user/settings`, {
            headers: { Authorization: `Bearer ${token}` },
        }, timeoutMs);

        if (!res.ok) return DEFAULT_SETTINGS;

        const data = await res.json();
        return { ...DEFAULT_SETTINGS, ...data };
    } catch (err: any) {
        if (err.name === "AbortError") {
            console.error(`取得系統設定超時 (${timeoutMs} ms)`);
        } else {
            console.error("取得系統設定失敗", err);
        }
        return DEFAULT_SETTINGS;
    }
}

// 更新使用者設定
export async function updateSystemSettings(
    settings: Partial<SystemSettings>,
    timeoutMs = 10000
) {
    if (!auth.currentUser) return false;

    const token = await auth.currentUser.getIdToken();

    try {
        const res = await fetchWithTimeout(`${BASE_URL}/user/settings`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(settings),
        }, timeoutMs);
        const data = await res.json();
        console.log("更新系統", data)

        return data
    } catch (err: any) {
        if (err.name === "AbortError") {
            console.error(`更新系統設定超時 (${timeoutMs} ms)`);
        } else {
            console.error("更新系統設定失敗", err);
        }
        return false;
    }
}