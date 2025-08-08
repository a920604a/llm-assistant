import React, { useState } from 'react'

const ChatPage = () => {
    const [messages, setMessages] = useState<{ role: 'user' | 'bot'; content: string }[]>([])
    const [input, setInput] = useState('')

    const handleSend = () => {
        if (!input.trim()) return
        setMessages([...messages, { role: 'user', content: input }])
        setInput('')
        // TODO: 呼叫 API 取得 bot 回覆，並加入 messages
    }

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-auto p-4 space-y-3 bg-white rounded shadow">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`p-3 rounded ${msg.role === 'user' ? 'bg-blue-100 self-end' : 'bg-gray-200 self-start'
                            } max-w-md`}
                    >
                        {msg.content}
                    </div>
                ))}
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
                >
                    送出
                </button>
            </div>
        </div>
    )
}

export default ChatPage
