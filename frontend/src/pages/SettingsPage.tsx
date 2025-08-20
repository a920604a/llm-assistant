import { useEffect, useState } from "react";
import { getSystemSettings, updateSystemSettings, SystemSettings } from "../api/settings";

export default function SettingsPage() {
    const [settings, setSettings] = useState<SystemSettings | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getSystemSettings().then((s) => {
            setSettings(s);
            setLoading(false);
        });
    }, []);

    const handleChange = (key: keyof SystemSettings, value: any) => {
        if (!settings) return;
        setSettings({ ...settings, [key]: value });
    };

    const handleSave = async () => {
        if (!settings) return;
        const ok = await updateSystemSettings(settings);
        if (ok) alert("設定已更新");
        else alert("更新失敗");
    };

    if (loading || !settings)
        return (
            <div className="flex justify-center items-center h-full text-gray-500">
                Loading...
            </div>
        );

    return (
        <div className="max-w-3xl mx-auto p-6 bg-gray-50 rounded-lg shadow-md mt-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">使用者設定</h2>

            <div className="grid grid-cols-1 gap-4">
                <div className="flex flex-col">
                    <label className="mb-1 font-medium text-gray-700">使用者語言</label>
                    <select
                        value={settings.user_language}
                        onChange={e => handleChange("user_language", e.target.value)}
                        className="p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                    >
                        <option value="en">English</option>
                        <option value="zh">中文</option>
                    </select>
                </div>

                <div className="flex items-center justify-between p-2 border rounded hover:bg-gray-100">
                    <span>自動翻譯</span>
                    <input
                        type="checkbox"
                        checked={settings.translate}
                        onChange={e => handleChange("translate", e.target.checked)}
                        className="h-5 w-5"
                    />
                </div>

                <div className="flex flex-col">
                    <label className="mb-1 font-medium text-gray-700">系統 Prompt</label>
                    <textarea
                        value={settings.system_prompt}
                        onChange={e => handleChange("system_prompt", e.target.value)}
                        className="p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                        rows={3}
                    />
                </div>

                <div className="flex flex-col">
                    <label className="mb-1 font-medium text-gray-700">檢索 Top-K</label>
                    <input
                        type="number"
                        value={settings.top_k}
                        onChange={e => handleChange("top_k", parseInt(e.target.value))}
                        className="p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                </div>

                <div className="flex items-center justify-between p-2 border rounded hover:bg-gray-100">
                    <span>使用 RAG</span>
                    <input
                        type="checkbox"
                        checked={settings.use_rag}
                        onChange={e => handleChange("use_rag", e.target.checked)}
                        className="h-5 w-5"
                    />
                </div>

                <div className="flex items-center justify-between p-2 border rounded hover:bg-gray-100">
                    <span>訂閱每日 Email</span>
                    <input
                        type="checkbox"
                        checked={settings.subscribe_email}
                        onChange={e => handleChange("subscribe_email", e.target.checked)}
                        className="h-5 w-5"
                    />
                </div>

                <div className="flex items-center justify-between p-2 border rounded hover:bg-gray-100">
                    <span>Reranker</span>
                    <input
                        type="checkbox"
                        checked={settings.reranker_enabled}
                        onChange={e => handleChange("reranker_enabled", e.target.checked)}
                        className="h-5 w-5"
                    />
                </div>
            </div>

            <div className="mt-6 flex justify-end">
                <button
                    onClick={handleSave}
                    className="px-6 py-2 bg-blue-600 text-white font-semibold rounded hover:bg-blue-700 transition"
                >
                    儲存設定
                </button>
            </div>
        </div>
    );
}
