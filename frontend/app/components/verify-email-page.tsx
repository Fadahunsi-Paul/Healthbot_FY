"use client"

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CheckCircle, XCircle, Loader2, Mail } from 'lucide-react'
import { buildUrl } from '@/app/config/api'

export default function VerifyEmailPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading')
  const [message, setMessage] = useState('')
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')

  useEffect(() => {
    const statusParam = searchParams.get('status')
    
    if (statusParam) {
      // Handle direct redirects from backend
      switch (statusParam) {
        case 'success':
          setStatus('success')
          setMessage('Email verified successfully!')
          return
        case 'expired':
          setStatus('expired')
          setMessage('Email activation link has expired. Please request a new verification email.')
          return
        case 'invalid':
          setStatus('error')
          setMessage('Invalid verification link.')
          return
      }
    }
    
    if (!token) {
      setStatus('error')
      setMessage('No verification token provided')
      return
    }

    verifyEmail(token)
  }, [token, searchParams])

  const verifyEmail = async (token: string) => {
    try {
      const response = await fetch(buildUrl(`/auth/verify-email/?token=${token}`), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      const data = await response.json()

      if (response.ok && data.status === 'success') {
        setStatus('success')
        setMessage(data.message || 'Email verified successfully!')
      } else if (data.status === 'expired') {
        setStatus('expired')
        setMessage(data.error || 'Email activation link has expired.')
      } else {
        setStatus('error')
        setMessage(data.error || 'Email verification failed')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  const handleResendVerification = () => router.push('/sign-up')
  const handleGoToLogin = () => router.push('/sign-in')

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
            <p className="text-lg font-medium">Verifying your email...</p>
            <p className="text-sm text-gray-600">Please wait while we verify your email address.</p>
          </div>
        )
      case 'success':
        return (
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-600" />
            <p className="text-lg font-medium text-green-600">Email Verified!</p>
            <p className="text-sm text-gray-600 text-center">{message}</p>
            <Button onClick={handleGoToLogin} className="w-full">
              Continue to Login
            </Button>
          </div>
        )
      case 'expired':
        return (
          <div className="flex flex-col items-center space-y-4">
            <XCircle className="h-12 w-12 text-orange-600" />
            <p className="text-lg font-medium text-orange-600">Link Expired</p>
            <p className="text-sm text-gray-600 text-center">{message}</p>
            <div className="flex flex-col space-y-2 w-full">
              <Button onClick={handleResendVerification} variant="outline" className="w-full">
                Request New Verification Email
              </Button>
              <Button onClick={handleGoToLogin} className="w-full">
                Go to Login
              </Button>
            </div>
          </div>
        )
      case 'error':
        return (
          <div className="flex flex-col items-center space-y-4">
            <XCircle className="h-12 w-12 text-red-600" />
            <p className="text-lg font-medium text-red-600">Verification Failed</p>
            <p className="text-sm text-gray-600 text-center">{message}</p>
            <div className="flex flex-col space-y-2 w-full">
              <Button onClick={handleResendVerification} variant="outline" className="w-full">
                Try Again
              </Button>
              <Button onClick={handleGoToLogin} className="w-full">
                Go to Login
              </Button>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Mail className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Email Verification
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            We're verifying your email address
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-center">Verification Status</CardTitle>
            <CardDescription className="text-center">
              {status === 'loading' && 'Please wait...'}
              {status === 'success' && 'Your email has been verified'}
              {status === 'expired' && 'Your verification link has expired'}
              {status === 'error' && 'Verification failed'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderContent()}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
