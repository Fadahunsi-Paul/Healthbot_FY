// Authentication utilities for the frontend
import { API_CONFIG, buildUrl } from "@/app/config/api"

// Types
export interface User {
  email: string
  first_name: string
  last_name: string
  is_verified: boolean
}

export interface LoginResponse {
  message: string
  access: string
  refresh: string
  user: User
}

export interface RegisterResponse {
  message: string
  user: User
}

// API Functions
export const authAPI = {
  // Register a new user
  register: async (userData: {
    first_name: string
    last_name: string
    email: string
    password: string
    confirm_password: string
  }): Promise<RegisterResponse> => {
    const response = await fetch(buildUrl(API_CONFIG.ENDPOINTS.REGISTER), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.error || "Registration failed")
    }
    
    return data
  },

  // Login user
  login: async (credentials: {
    email: string
    password: string
  }): Promise<LoginResponse> => {
    const response = await fetch(buildUrl(API_CONFIG.ENDPOINTS.LOGIN), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.error || "Login failed")
    }
    
    return data
  },

  // Logout user
  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem("refresh_token")
    
    if (refreshToken) {
      try {
        await fetch(buildUrl(API_CONFIG.ENDPOINTS.LOGOUT), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getAccessToken()}`,
          },
          body: JSON.stringify({ refresh: refreshToken }),
        })
      } catch (error) {
        console.error("Logout error:", error)
      }
    }
    
    // Clear local storage
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user_data")
  },

  // Refresh access token
  refreshToken: async (): Promise<string> => {
    const refreshToken = localStorage.getItem("refresh_token")
    
    if (!refreshToken) {
      throw new Error("No refresh token available")
    }

    const response = await fetch(buildUrl(API_CONFIG.ENDPOINTS.REFRESH_TOKEN), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refreshToken }),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error("Token refresh failed")
    }

    localStorage.setItem("access_token", data.access)
    return data.access
  },

  // Update user profile
  updateProfile: async (profileData: any): Promise<any> => {
    // Filter out null/undefined values to avoid validation issues
    const filteredData = Object.fromEntries(
      Object.entries(profileData).filter(([_, value]) => value !== null && value !== undefined)
    )
    
    console.log('Filtered profile data being sent:', filteredData)
    
    const response = await authenticatedFetch(buildUrl(API_CONFIG.ENDPOINTS.PROFILE_UPDATE), {
      method: "PUT",
      body: JSON.stringify(filteredData),
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.error || "Profile update failed")
    }

    // Update stored user data (only the basic user info, not the full profile)
    const basicUserData = {
      email: data.user.email,
      first_name: data.user.first_name,
      last_name: data.user.last_name,
      is_verified: data.user.is_verified
    }
    localStorage.setItem("user_data", JSON.stringify(basicUserData))
    
    return data
  },

  // Get complete user profile
  getProfile: async (): Promise<any> => {
    const response = await authenticatedFetch(buildUrl(API_CONFIG.ENDPOINTS.PROFILE_UPDATE), {
      method: "GET",
    })

    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.error || "Failed to get profile")
    }
    
    return data
  },
}

// Token management
export const getAccessToken = (): string | null => {
  return localStorage.getItem("access_token")
}

export const getRefreshToken = (): string | null => {
  return localStorage.getItem("refresh_token")
}

export const getUserData = (): User | null => {
  const userData = localStorage.getItem("user_data")
  return userData ? JSON.parse(userData) : null
}

export const isAuthenticated = (): boolean => {
  return !!getAccessToken()
}

// Authenticated fetch wrapper
export const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  let accessToken = getAccessToken()

  // If no access token, throw error
  if (!accessToken) {
    throw new Error("Not authenticated")
  }

  // Add authorization header
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
    Authorization: `Bearer ${accessToken}`,
  }

  let response = await fetch(url, {
    ...options,
    headers,
  })

  // If token expired, try to refresh
  if (response.status === 401) {
    try {
      accessToken = await authAPI.refreshToken()
      
      // Retry with new token
      response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          Authorization: `Bearer ${accessToken}`,
        },
      })
    } catch (error) {
      // Refresh failed, redirect to login
      authAPI.logout()
      throw new Error("Authentication expired")
    }
  }

  return response
}

// Chat API with authentication
export const chatAPI = {
  // Send message to health chatbot with session support
  sendMessage: async (question: string, sessionId?: string): Promise<any> => {
    const payload: any = { question }
    if (sessionId) {
      payload.session_id = sessionId
    }

    const response = await authenticatedFetch(buildUrl(API_CONFIG.ENDPOINTS.CHATBOT), {
      method: "POST",
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error("Failed to send message")
    }

    return response.json()
  },

  // Get list of chat sessions
  getChatSessions: async (): Promise<any[]> => {
    const response = await authenticatedFetch(buildUrl(API_CONFIG.ENDPOINTS.CHAT_SESSIONS), {
      method: "GET",
    })

    if (!response.ok) {
      throw new Error("Failed to get chat sessions")
    }

    return response.json()
  },

  // Get chat history for a specific session
  getChatHistory: async (sessionId: string): Promise<any[]> => {
    const response = await authenticatedFetch(buildUrl(`${API_CONFIG.ENDPOINTS.CHAT_HISTORY}${sessionId}/`), {
      method: "GET",
    })

    if (!response.ok) {
      throw new Error("Failed to get chat history")
    }

    return response.json()
  },

  // Delete a chat session
  deleteSession: async (sessionId: string): Promise<void> => {
    const response = await authenticatedFetch(buildUrl(`${API_CONFIG.ENDPOINTS.DELETE_CHAT_SESSION}${sessionId}/delete/`), {
      method: "DELETE",
    })

    if (!response.ok) {
      throw new Error("Failed to delete chat session")
    }
  },

  // Upload audio to chatbot endpoint with optional session support
  uploadAudio: async (file: File, sessionId?: string): Promise<any> => {
    let accessToken = getAccessToken()
    if (!accessToken) {
      throw new Error("Not authenticated")
    }

    const formData = new FormData()
    formData.append("audio", file)
    if (sessionId) {
      formData.append("session_id", sessionId)
    }

    // Note: don't set Content-Type so browser sets multipart boundary
    const url = buildUrl(API_CONFIG.ENDPOINTS.CHAT_AUDIO)
    let response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: formData,
    })

    if (response.status === 401) {
      try {
        accessToken = await authAPI.refreshToken()
        response = await fetch(url, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          body: formData,
        })
      } catch (error) {
        authAPI.logout()
        throw new Error("Authentication expired")
      }
    }

    if (!response.ok) {
      const errorText = await response.text().catch(() => "")
      throw new Error(errorText || "Failed to upload audio")
    }

    return response.json()
  },
}

export default authAPI