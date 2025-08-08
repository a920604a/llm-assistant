import React from 'react'

const UploadPage = () => {
    return (
        <div>
            <h2 className="text-2xl font-semibold mb-4">上傳你的筆記</h2>
            <div className="border-2 border-dashed border-gray-400 rounded p-12 text-center text-gray-600 cursor-pointer hover:bg-gray-100">
                點擊或拖曳檔案到此處 (支援 Markdown / PDF / 資料夾)
            </div>
            {/* 這裡可以後續擴充上傳進度與狀態顯示 */}
        </div>
    )
}

export default UploadPage
