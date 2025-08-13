import { auth } from "../firebase" // 假設你這樣匯入 firebase auth
import { BASE_URL } from "./conf";

export async function uploadFiles(files: FileList | File[]): Promise<{ message: string; files: string[] } | null> {
    if (!auth.currentUser) return null

    const token = await auth.currentUser.getIdToken()
    console.log("token", token)

    const formData = new FormData()
    if ("length" in files) {
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i])
        }
    } else {
        formData.append("files", files)
    }

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
