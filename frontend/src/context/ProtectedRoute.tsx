import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'  // 假設你有自訂 Hook 取得使用者登入狀態

interface Props {
    children: React.ReactNode
}

export default function ProtectedRoute({ children }: Props) {
    const { user, loading } = useAuth()

    if (loading) {
        return <div>載入中...</div>  // 等待登入狀態確認時顯示
    }

    if (!user) {
        return <Navigate to="/login" replace />
    }

    return <>{children}</>
}
