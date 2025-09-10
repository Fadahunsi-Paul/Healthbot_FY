"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Activity, ArrowLeft, Heart, Stethoscope, Plus, Pill, Zap, Shield, Loader2 } from "lucide-react"

import { API_CONFIG, buildUrl } from "@/app/config/api"

interface SignUpPageProps {
  onSignUp: (userData: { name: string; email: string; password: string }) => void
  onNavigate: (page: "landing" | "signup" | "signin" | "chat") => void
}

export default function SignUpPage({ onSignUp, onNavigate }: SignUpPageProps) {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors: Record<string, string> = {}

    if (!formData.fullName.trim()) newErrors.fullName = "Full name is required"
    if (!formData.email.trim()) newErrors.email = "Email is required"
    if (!formData.password) newErrors.password = "Password is required"
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match"
    }
    if (formData.password && formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters"
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      setIsLoading(true)
      setSuccessMessage("")
      
      try {
        // Split full name into first and last name
        const nameParts = formData.fullName.trim().split(" ")
        const firstName = nameParts[0]
        const lastName = nameParts.slice(1).join(" ") || "User"

        const response = await fetch(buildUrl(API_CONFIG.ENDPOINTS.REGISTER), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            email: formData.email.toLowerCase().trim(),
            password: formData.password,
            confirm_password: formData.confirmPassword,
          }),
        })

        const data = await response.json()

        if (response.ok) {
          setSuccessMessage(data.message || "Registration successful! Please check your email to verify your account.")
          // Clear form
          setFormData({
            fullName: "",
            email: "",
            password: "",
            confirmPassword: "",
          })
          // Auto-navigate to sign-in after 2 seconds
          setTimeout(() => {
            onNavigate("signin")
          }, 2000)
        } else {
          setErrors({ general: data.error || "Registration failed. Please try again." })
        }
      } catch (error) {
        console.error("Registration error:", error)
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
          <CardTitle className="text-2xl font-bold text-gray-900">Create Account</CardTitle>
          <p className="text-gray-600">Join HealthBot for personalized health insights</p>
        </CardHeader>
        <CardContent>
          {successMessage && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-700 text-sm">{successMessage}</p>
            </div>
          )}
          
          {errors.general && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700 text-sm">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                className={errors.fullName ? "border-red-500" : ""}
                disabled={isLoading}
              />
              {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>}
            </div>

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
              <Label htmlFor="password">Password (min 8 characters)</Label>
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

            <div>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className={errors.confirmPassword ? "border-red-500" : ""}
                disabled={isLoading}
              />
              {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Account...
                </>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Already have an account?{" "}
              <button onClick={() => onNavigate("signin")} className="text-blue-600 hover:underline font-medium">
                Sign In
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
