import React from 'react'
import Sidebar from '../components/Sidebar'
import { Outlet } from 'react-router-dom'
import Auth from '../components/Auth'  // <- 引入 Auth 元件

const MainLayout = () => {
    return (
        <div className="flex h-screen bg-gray-100">
            <Sidebar />
            <div className="flex flex-col flex-1">
                <header className="h-14 bg-white shadow flex items-center justify-between px-6">
                    <h1 className="text-xl font-semibold text-gray-800">星河安夜的筆記平台</h1>
                    <Auth />  {/* 放在 header 右邊 */}
                </header>
                <main className="flex-1 overflow-auto p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

export default MainLayout
