import React, { useState, useRef } from "react"
import { uploadFiles } from "../api/upload"

interface UploadState {
    uploading: boolean;
    message: string;
    files: string[];
}



const UploadPage = () => {
    // const [uploading, setUploading] = useState(false)
    // const [message, setMessage] = useState("")


    const [uploadState, setUploadState] = useState<UploadState>({
        uploading: false,
        message: "",
        files: [],
    });


    const fileInputRef = useRef<HTMLInputElement | null>(null)

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        // setUploading(true)

        setUploadState({ ...uploadState, uploading: true, message: "上傳中..." });
        // setMessage("上傳中...")

        try {
            const result = await uploadFiles(files)
            if (result) {
                setUploadState({
                    uploading: false,
                    message: result.message,
                    files: result.files,
                });
            } else {
                setUploadState({
                    uploading: false,
                    message: "尚未登入或無法取得使用者資訊",
                    files: [],
                });
            }
            // result message, files = []
        } catch (error) {
            setUploadState({
                uploading: false,
                message: `上傳失敗: ${(error as Error).message}`,
                files: [],
            });
        } finally {
            if (fileInputRef.current) {
                fileInputRef.current.value = ""; // 重置 input
            }
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
                    ref={fileInputRef}  // 綁定 ref
                    type="file"
                    multiple
                    accept=".md"
                    onChange={handleFileChange}
                    className="hidden"
                />
            </label>
            {uploadState.uploading && <p className="mt-2 text-blue-600">{uploadState.message}</p>}
            {/* {!uploading && message && <p className="mt-2">{message}</p>} */}
            {!uploadState.uploading && uploadState.message && (
                <div className="mt-2">
                    <p>{uploadState.message}</p>
                    {uploadState.files?.length > 0 && (
                        <ul className="list-disc ml-5 mt-1">
                            {uploadState.files.map((file) => (
                                <li key={file}>{file}</li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    )
}

export default UploadPage
