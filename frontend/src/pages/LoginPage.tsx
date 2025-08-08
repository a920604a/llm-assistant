import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, loginWithGoogle } from '../firebase';
import { onAuthStateChanged } from 'firebase/auth';

export default function LoginPage() {
    const navigate = useNavigate();

    // 🔄 若已登入，直接導向主頁
    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            if (user) {
                const token = await user.getIdToken();
                localStorage.setItem("idToken", token); // ✅ 儲存 token
                navigate('/', { replace: true });
            }
        });
        return () => unsubscribe();
    }, [navigate]);

    // 🔐 點擊登入按鈕
    const handleLogin = async () => {
        try {
            const result = await loginWithGoogle();
            const user = result.user;
            const token = await user.getIdToken();
            localStorage.setItem("idToken", token); // ✅ 儲存 token

            navigate('/', { replace: true });
        } catch (error) {
            console.error("登入失敗：", error);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
            <h1 className="text-3xl font-bold mb-6">請先登入</h1>
            <button
                onClick={handleLogin}
                className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition"
            >
                使用 Google 登入
            </button>
        </div>
    );
}
