"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Activity, ArrowLeft, Heart, Stethoscope, Plus, Pill, Zap, Shield, Loader2 } from "lucide-react"

import { API_CONFIG, buildUrl } from "@/app/config/api"

interface SignInPageProps {
  onSignIn: (credentials: { email: string; password: string }) => void
  onNavigate: (page: "landing" | "signup" | "signin" | "chat") => void
}

export default function SignInPage({ onSignIn, onNavigate }: SignInPageProps) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors: Record<string, string> = {}

    if (!formData.email.trim()) newErrors.email = "Email is required"
    if (!formData.password) newErrors.password = "Password is required"

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      setIsLoading(true)
      
      try {
        const response = await fetch(buildUrl(API_CONFIG.ENDPOINTS.LOGIN), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: formData.email.toLowerCase().trim(),
            password: formData.password,
          }),
        })

        const data = await response.json()

        if (response.ok) {
          // Store JWT tokens in localStorage
          localStorage.setItem("access_token", data.access)
          localStorage.setItem("refresh_token", data.refresh)
          localStorage.setItem("user_data", JSON.stringify(data.user))
          
          // Call the original onSignIn callback for compatibility
          onSignIn(formData)
          
          // Navigate to chat
          onNavigate("chat")
        } else {
          setErrors({ general: data.error || "Login failed. Please check your credentials." })
        }
      } catch (error) {
        console.error("Login error:", error)
        setErrors({ general: "Network error. Please check your connection and try again." })
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800">
        {/* Moving Medical Items */}
        <div className="absolute inset-0">
          {/* Floating Hearts */}
          <div className="absolute top-20 left-10 text-red-300/20 animate-float-slow">
            <Heart className="w-8 h-8" fill="currentColor" />
          </div>
          <div className="absolute top-40 right-20 text-red-300/15 animate-float-medium">
            <Heart className="w-6 h-6" fill="currentColor" />
          </div>
          <div className="absolute bottom-32 left-1/4 text-red-300/25 animate-float-fast">
            <Heart className="w-10 h-10" fill="currentColor" />
          </div>

          {/* Floating Stethoscopes */}
          <div className="absolute top-1/3 left-20 text-blue-200/20 animate-drift-right">
            <Stethoscope className="w-12 h-12" />
          </div>
          <div className="absolute bottom-1/4 right-32 text-blue-200/15 animate-drift-left">
            <Stethoscope className="w-8 h-8" />
          </div>

          {/* Medical Crosses */}
          <div className="absolute top-60 right-10 text-green-300/20 animate-bounce-slow">
            <Plus className="w-10 h-10" />
          </div>
          <div className="absolute bottom-20 left-32 text-green-300/15 animate-bounce-slow">
            <Plus className="w-6 h-6" />
          </div>

          {/* Pills */}
          <div className="absolute top-80 left-1/3 text-yellow-300/20 animate-spin-slow">
            <Pill className="w-8 h-8" />
          </div>
          <div className="absolute bottom-40 right-1/4 text-yellow-300/15 animate-spin-slow">
            <Pill className="w-6 h-6" />
          </div>

          {/* Activity/Pulse Icons */}
          <div className="absolute top-1/2 left-10 text-cyan-300/20 animate-pulse">
            <Activity className="w-10 h-10" />
          </div>
          <div className="absolute bottom-60 right-40 text-cyan-300/15 animate-pulse">
            <Activity className="w-8 h-8" />
          </div>

          {/* Shield Icons */}
          <div className="absolute top-32 right-1/3 text-purple-300/20 animate-float-medium">
            <Shield className="w-9 h-9" />
          </div>
          <div className="absolute bottom-80 left-40 text-purple-300/15 animate-float-slow">
            <Shield className="w-7 h-7" />
          </div>

          {/* DNA Helix (using Zap as substitute) */}
          <div className="absolute top-1/4 right-20 text-pink-300/20 animate-wiggle">
            <Zap className="w-8 h-8" />
          </div>
          <div className="absolute bottom-1/3 left-1/2 text-pink-300/15 animate-wiggle">
            <Zap className="w-6 h-6" />
          </div>
        </div>

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-900/20 to-purple-900/30"></div>
      </div>

      <Card className="w-full max-w-md relative z-10 shadow-2xl backdrop-blur-sm bg-white/95">
        <CardHeader className="text-center pb-2">
          <div className="flex items-center justify-center mb-4">
            <Button variant="ghost" size="icon" className="absolute left-4 top-4" onClick={() => onNavigate("landing")}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">Welcome Back</CardTitle>
          <p className="text-gray-600">Sign in to continue your health journey</p>
        </CardHeader>
        <CardContent>
          {errors.general && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700 text-sm">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={errors.email ? "border-red-500" : ""}
                disabled={isLoading}
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className={errors.password ? "border-red-500" : ""}
                disabled={isLoading}
              />
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Don't have an account?{" "}
              <button onClick={() => onNavigate("signup")} className="text-blue-600 hover:underline font-medium">
                Sign Up
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
