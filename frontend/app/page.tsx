"use client"

import { useState, useEffect } from "react"
import LandingPage from "./components/landing-page"
import SignUpPage from "./sign-up/page"
import SignInPage from "./sign-in/page"
import ChatInterface from "./components/chat-interface"
import ProfilePage from "./components/profile-page"
import { authAPI, getUserData, isAuthenticated, User } from "./utils/auth"

type Page = "landing" | "signup" | "signin" | "chat" | "profile"

interface AppUser {
  name: string
  email: string
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("landing")
  const [user, setUser] = useState<AppUser | null>(null)

  // Helper function to convert backend User to AppUser
  const convertUserToAppUser = (backendUser: User): AppUser => {
    return {
      name: `${backendUser.first_name} ${backendUser.last_name}`.trim(),
      email: backendUser.email
    }
  }

  // Check for existing authentication on app load
  useEffect(() => {
    if (isAuthenticated()) {
      const userData = getUserData()
      if (userData) {
        setUser(convertUserToAppUser(userData))
        setCurrentPage("chat")
      }
    }
  }, [])

  const handleSignUp = async (userData: { name: string; email: string; password: string }) => {
    try {
      // Split the name into first and last name
      const nameParts = userData.name.trim().split(' ')
      const firstName = nameParts[0] || ''
      const lastName = nameParts.slice(1).join(' ') || ''
      
      const response = await authAPI.register({
        first_name: firstName,
        last_name: lastName,
        email: userData.email,
        password: userData.password,
        confirm_password: userData.password
      })
      
      // Store user data and redirect to chat
      const appUser = convertUserToAppUser(response.user)
      setUser(appUser)
      localStorage.setItem("user_data", JSON.stringify(response.user))
      setCurrentPage("chat")
    } catch (error) {
      console.error("Sign up error:", error)
      // Handle error (you might want to show an error message to the user)
    }
  }

  const handleSignIn = async (credentials: { email: string; password: string }) => {
    try {
      const response = await authAPI.login(credentials)
      
      // Store tokens and user data
      localStorage.setItem("access_token", response.access)
      localStorage.setItem("refresh_token", response.refresh)
      localStorage.setItem("user_data", JSON.stringify(response.user))
      
      // Set user state and redirect to chat
      const appUser = convertUserToAppUser(response.user)
      setUser(appUser)
      setCurrentPage("chat")
    } catch (error) {
      console.error("Sign in error:", error)
      // Handle error (you might want to show an error message to the user)
    }
  }

  const handleSignOut = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error("Sign out error:", error)
    } finally {
      // Always clear user state and redirect
      setUser(null)
      setCurrentPage("landing")
    }
  }

  const renderPage = () => {
    switch (currentPage) {
      case "landing":
        return <LandingPage onNavigate={setCurrentPage} />
      case "signup":
        return <SignUpPage onSignUp={handleSignUp} onNavigate={setCurrentPage} />
      case "signin":
        return <SignInPage onSignIn={handleSignIn} onNavigate={setCurrentPage} />
      case "chat":
        return user ? <ChatInterface user={user} onSignOut={handleSignOut} onNavigate={setCurrentPage} /> : null
      case "profile":
        return user ? (
          <ProfilePage
            user={user}
            onBack={() => setCurrentPage("chat")}
            onUpdateProfile={(userData) => {
              setUser({ ...user, ...userData })
              // Don't automatically redirect - let the profile page handle navigation
            }}
          />
        ) : null
      default:
        return <LandingPage onNavigate={setCurrentPage} />
    }
  }

  return <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">{renderPage()}</div>
}
