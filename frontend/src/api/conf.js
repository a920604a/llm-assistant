// export const BASE_URL = "/api";  // 改成統一使用 Nginx API Gateway 的路徑
export const BASE_URL = import.meta.env.VITE_API_URL;


// WebSocket Gateway
// export const WS_URL = "/ws";