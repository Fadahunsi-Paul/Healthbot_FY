// API Configuration
export const API_CONFIG = {
  // Backend URL - change this to your deployed backend URL in production
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || "https://healthbot-fy.onrender.com",
  //  BASE_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",

  
  // API Endpoints
  ENDPOINTS: {
    REGISTER: "/auth/register/",
    LOGIN: "/auth/login/", 
    LOGOUT: "/auth/logout/",
    REFRESH_TOKEN: "/auth/token/refresh/",
    VERIFY_EMAIL: "/auth/verify-email/",
    PASSWORD_RESET_REQUEST: "/auth/request-password-reset/",
    PASSWORD_RESET: "/auth/password-reset/",
    PROFILE_UPDATE: "/auth/profile/",
    CHAT: "/api/chat/",
    CHATBOT: "/api/chatbot/",
    CHAT_SESSIONS: "/api/chat-sessions/",
    CHAT_HISTORY: "/api/chat-sessions/",
    DELETE_CHAT_SESSION: "/api/chat-sessions/",
    CHAT_AUDIO: "/api/chat/audio/",
    DAILY_TIP: "/api/daily-tip/",
  },
  
  // Request timeouts
  TIMEOUTS: {
    DEFAULT: 10000, // 10 seconds
    UPLOAD: 30000,  // 30 seconds
  },
  
  // Headers
  HEADERS: {
    JSON: {
      "Content-Type": "application/json",
    },
  },
}

// Helper to build full URLs
export const buildUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}

export default API_CONFIG