import { useEffect, useState } from "react";
import { auth, loginWithGoogle, logout } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";

export default function Auth() {
    const [user, setUser] = useState<null | { displayName: string; email: string }>(null);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            if (currentUser) {
                setUser({ displayName: currentUser.displayName ?? "", email: currentUser.email ?? "" });
            } else {
                setUser(null);
            }
        });
        return () => unsubscribe();
    }, []);

    if (!user) {
        return (
            <button
                className="bg-blue-600 text-white px-4 py-2 rounded"
                onClick={() => loginWithGoogle()}
            >
                使用 Google 登入
            </button>
        );
    }

    return (
        <div className="flex items-center space-x-4">
            <span>歡迎, {user.displayName}</span>
            <button
                className="bg-red-600 text-white px-3 py-1 rounded"
                onClick={() => logout()}
            >
                登出
            </button>
        </div>
    );
}
