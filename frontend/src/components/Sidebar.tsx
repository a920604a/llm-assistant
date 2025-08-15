import React from 'react'
import { NavLink } from 'react-router-dom'

const navItems = [
    { to: '/', label: 'Dashboard' },
    { to: '/upload', label: '上傳筆記' },
    { to: '/notes', label: '我的筆記' },
    { to: '/chat', label: 'Chat 機器人' },
    { to: '/history', label: '歷史紀錄' },
    { to: '/settings', label: '設定' },
]

const Sidebar = () => {
    return (
        <aside className="w-60 bg-gray-800 text-white flex flex-col">
            <div className="h-14 flex items-center justify-center text-2xl font-bold border-b border-gray-700">
                未來放logo 地方
            </div>
            <nav className="flex-1 p-4 space-y-2">
                {navItems.map(({ to, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        className={({ isActive }) =>
                            `block px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-700' : 'hover:bg-gray-700/50'
                            }`
                        }
                    >
                        {label}
                    </NavLink>
                ))}
            </nav>
        </aside>
    )
}

export default Sidebar
