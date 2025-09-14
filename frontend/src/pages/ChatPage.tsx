import { useState, useRef, useEffect } from 'react';
import { ask } from "../api/ask";

type Message = {
    role: 'user' | 'bot';
    content: string;
    timestamp?: string;
}

const ChatPage = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    // 自動捲動到底部
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', content: input, timestamp: new Date().toISOString() };
        const botMessage: Message = { role: 'bot', content: '', timestamp: new Date().toISOString() };

        setMessages(prev => [...prev, userMessage, botMessage]);
        setInput('');
        setLoading(true);

        try {
            await ask(input, "standard", (chunk) => {
                setMessages(prev => {
                    const newMsgs = [...prev];
                    const lastMsg = newMsgs[newMsgs.length - 1];
                    newMsgs[newMsgs.length - 1] = {
                        ...lastMsg,
                        content: (lastMsg.content || "") + chunk,  // 累加
                    };
                    return newMsgs;
                });
            });

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'bot', content: '❌ 發生錯誤，請稍後再試', timestamp: new Date().toISOString() }]);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex flex-col h-full p-4">
            <h2 className="text-2xl font-semibold mb-4">聊天訊息</h2>

            <div className="flex-1 overflow-auto flex flex-col space-y-3">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`p-3 rounded max-w-md whitespace-pre-wrap
                            ${msg.role === 'user'
                                ? 'bg-blue-100 self-end shadow'
                                : 'bg-gray-200 self-start shadow-sm'
                            }`}
                    >
                        {msg.timestamp && (
                            <div className="text-sm text-gray-500 mb-1">
                                {new Date(msg.timestamp).toLocaleString()}
                            </div>
                        )}
                        <div>{msg.content}</div>
                    </div>
                ))}
                {loading && (
                    <div className="text-gray-500">⏳ LLM 思考中...</div>
                )}
                <div ref={bottomRef} />
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
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    disabled={loading}
                >
                    送出
                </button>
            </div>
        </div>
    )
}

export default ChatPage;
