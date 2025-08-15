import { auth } from "../firebase" // 假設你這樣匯入 firebase auth
import { BASE_URL } from "./conf";

export async function uploadFiles(files: FileList | File[]): Promise<{ message: string; files: string[] } | null> {
    if (!auth.currentUser) return null

    const token = await auth.currentUser.getIdToken()
    console.log("token", token)

    const formData = new FormData()

    // 統一用 Array.from 將 FileList 轉成陣列
    Array.from(files).forEach((file) => {
        formData.append("files", file)
    })



    const response = await fetch(`${BASE_URL}/upload`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
        },
        body: formData,
    })

    if (!response.ok) {
        throw new Error("上傳失敗")
    }

    return await response.json()
}
