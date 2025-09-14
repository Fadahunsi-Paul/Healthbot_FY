"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Mail, CheckCircle, Loader2 } from 'lucide-react'
import { buildUrl } from '@/app/config/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(buildUrl('/auth/request-password-reset/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email.toLowerCase().trim() }),
      })

      const data = await response.json()

      if (response.ok) {
        setIsSuccess(true)
      } else {
        setError(data.error || 'Failed to send reset code')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleBackToLogin = () => {
    router.push('/sign-in')
  }

  const handleTryAgain = () => {
    setIsSuccess(false)
    setEmail('')
    setError('')
  }

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Check Your Email
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              We've sent a reset code to your email address
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-center">Reset Code Sent</CardTitle>
              <CardDescription className="text-center">
                If your email is registered, a 6-digit reset code has been sent to:
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <p className="font-medium text-gray-900">{email}</p>
              </div>
              
              <Alert>
                <Mail className="h-4 w-4" />
                <AlertDescription>
                  Please check your email and enter the 6-digit code on the next page to reset your password.
                </AlertDescription>
              </Alert>

              <div className="flex flex-col space-y-2">
                <Button 
                  onClick={() => router.push(`/reset-password?email=${encodeURIComponent(email)}`)}
                  className="w-full"
                >
                  Enter Reset Code
                </Button>
                <Button 
                  onClick={handleTryAgain} 
                  variant="outline" 
                  className="w-full"
                >
                  Try Different Email
                </Button>
                <Button 
                  onClick={handleBackToLogin} 
                  variant="ghost" 
                  className="w-full"
                >
                  Back to Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Mail className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Forgot Password?
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Enter your email address and we'll send you a reset code
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">Reset Password</CardTitle>
            <CardDescription className="text-center">
              We'll send a 6-digit code to your email address
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  required
                  disabled={isLoading}
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading || !email.trim()}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending Code...
                  </>
                ) : (
                  'Send Reset Code'
                )}
              </Button>

              <Button 
                type="button" 
                onClick={handleBackToLogin} 
                variant="ghost" 
                className="w-full"
                disabled={isLoading}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
