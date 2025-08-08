// src/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
    apiKey: "AIzaSyBcz4BljMb-AwQ5S3wfAHwGW2t4V7FGURk",
    authDomain: "llm-assistant-c926b.firebaseapp.com",
    projectId: "llm-assistant-c926b",
    storageBucket: "llm-assistant-c926b.firebasestorage.app",
    messagingSenderId: "992781541331",
    appId: "1:992781541331:web:edd2588c8167b89bc95926",
    measurementId: "G-ESWYB6XPE5"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const provider = new GoogleAuthProvider();

export const loginWithGoogle = async () => {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    const idToken = await user.getIdToken(); // 🔐 拿到 JWT Token
    return { user, idToken };
};

export const logout = () => signOut(auth);
