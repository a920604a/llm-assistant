// ChatPage.tsx
import React, { useState } from 'react'
import { ask } from "../api/ask"

const ChatPage = () => {
    const [messages, setMessages] = useState<{ role: 'user' | 'bot'; content: string }[]>([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSend = async () => {
        if (!input.trim()) return

        const userMessage = { role: 'user' as const, content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const res = await ask(input) // 呼叫後端
            if (res && res.reply) {
                setMessages(prev => [...prev, { role: 'bot', content: res.reply }])
            } else {
                setMessages(prev => [...prev, { role: 'bot', content: '⚠️ 後端沒有回應' }])
            }
        } catch (error) {
            console.error(error)
            setMessages(prev => [...prev, { role: 'bot', content: '❌ 發生錯誤，請稍後再試' }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-auto p-4 space-y-3 bg-white rounded shadow">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`p-3 rounded ${msg.role === 'user'
                            ? 'bg-blue-100 self-end'
                            : 'bg-gray-200 self-start'} max-w-md`}
                    >
                        {msg.content}
                    </div>
                ))}
                {loading && <div className="text-gray-500">⏳ LLM 思考中...</div>}
            </div>
            <div className="mt-4 flex space-x-2">
                <input
                    className="flex-1 border rounded px-3 py-2"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="請輸入問題..."
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                />
                <button
                    onClick={handleSend}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    disabled={loading}
                >
                    送出
                </button>
            </div>
        </div>
    )
}

export default ChatPage
