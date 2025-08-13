import React, { useState } from "react"
import { uploadFiles } from "../api/upload"

const UploadPage = () => {
    const [uploading, setUploading] = useState(false)
    const [message, setMessage] = useState("")

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        setUploading(true)
        setMessage("上傳中...")

        try {
            const result = await uploadFiles(files)
            setMessage(`成功上傳 ${result.files.length} 個檔案`)
        } catch (error) {
            setMessage(`上傳失敗: ${(error as Error).message}`)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div>
            <h2 className="text-2xl font-semibold mb-4">上傳你的筆記</h2>
            <label
                htmlFor="file-upload"
                className="border-2 border-dashed border-gray-400 rounded p-12 text-center text-gray-600 cursor-pointer hover:bg-gray-100 block"
            >
                點擊或拖曳檔案到此處 (支援 Markdown / PDF / 資料夾)
                <input
                    id="file-upload"
                    type="file"
                    multiple
                    accept=".md"
                    onChange={handleFileChange}
                    className="hidden"
                />
            </label>
            {uploading && <p className="mt-2 text-blue-600">{message}</p>}
            {!uploading && message && <p className="mt-2">{message}</p>}
        </div>
    )
}

export default UploadPage
