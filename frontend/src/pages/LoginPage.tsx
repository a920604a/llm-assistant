import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, loginWithGoogle } from '../firebase';
import { onAuthStateChanged } from 'firebase/auth';

export default function LoginPage() {
    const navigate = useNavigate();

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            if (user) {
                // 如果已登入，自動導向首頁
                navigate('/', { replace: true });
            }
        });
        return () => unsubscribe();
    }, [navigate]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
            <h1 className="text-3xl font-bold mb-6">請先登入</h1>
            <button
                onClick={loginWithGoogle}
                className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition"
            >
                使用 Google 登入
            </button>


        </div>
    );
}
