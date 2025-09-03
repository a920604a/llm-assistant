import { auth } from "../firebase";
import { BASE_URL } from "./conf";

export interface ChatMessage {
    role: 'user' | 'bot'
    content: string
    timestamp: string
}

// 修正為 async function
export const getChatHistory = async (): Promise<ChatMessage[]> => {
    if (!auth.currentUser) return [] // 沒登入回傳空陣列

    try {
        const res = await fetch(`${BASE_URL}/chat/history`, {
            headers: {
                "Authorization": `Bearer ${await auth.currentUser.getIdToken()}`
            }
        })
        if (!res.ok) throw new Error('Failed to fetch chat history')
        const data = await res.json()
        return data as ChatMessage[]
    } catch (error) {
        console.error(error)
        return []
    }
}
