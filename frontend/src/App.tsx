import React from 'react'
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom'

import MainLayout from './layouts/MainLayout'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import HistoryPage from './pages/HistoryPage'
import SettingsPage from './pages/SettingsPage'

import LoginPage from './pages/LoginPage'  // 你需要建立這個登入頁面
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './context/ProtectedRoute'
import Auth from './components/Auth'  // 預計放在 MainLayout 的 header 裡

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 登入頁，公開路由 */}
          <Route path="/login" element={<LoginPage />} />

          {/* 主要路由，需登入才能訪問 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* 其餘路由導回首頁 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
