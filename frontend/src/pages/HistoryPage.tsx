import { useEffect, useState, useRef } from 'react'
import { getChatHistory, type ChatMessage } from '../api/chat'

const HistoryPage = () => {
    const [history, setHistory] = useState<ChatMessage[]>([]) // 初始值保證是陣列
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const bottomRef = useRef<HTMLDivElement>(null)

    // 抓取聊天歷史
    useEffect(() => {
        const fetchHistory = async () => {
            setLoading(true)
            try {
                const data = await getChatHistory()
                setHistory(data || []) // 保證是陣列
            } catch (err) {
                console.error(err)
                setError('❌ Failed to load chat history')
                setHistory([]) // 出錯也要保證 history 是陣列
            } finally {
                setLoading(false)
            }
        }
        fetchHistory()
    }, [])

    // 自動捲動到底部
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [history])

    return (
        <div className="p-4 flex flex-col h-full">
            <h2 className="text-2xl font-semibold mb-4">聊天歷史紀錄</h2>

            {loading && <p className="text-gray-500">⏳ Loading...</p>}
            {error && <p className="text-red-500">{error}</p>}

            {!loading && !error && history.length === 0 && (
                <p className="text-gray-400">目前沒有聊天紀錄</p>
            )}

            <div className="flex-1 overflow-auto flex flex-col space-y-3">
                {history.map((msg) => (
                    <div
                        key={msg.id}
                        className={`p-3 rounded max-w-md whitespace-pre-wrap ${msg.role === 'user'
                            ? 'bg-blue-100 self-end shadow'
                            : 'bg-gray-200 self-start shadow-sm'
                            }`}
                    >
                        <div className="text-sm text-gray-500 mb-1">
                            {new Date(msg.timestamp).toLocaleString()}
                        </div>
                        <div>{msg.content}</div>
                    </div>
                ))}
                {/* 用來自動捲動到底部 */}
                <div ref={bottomRef} />
            </div>
        </div>
    )
}

export default HistoryPage
