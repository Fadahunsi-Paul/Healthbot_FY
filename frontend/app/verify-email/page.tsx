import { Suspense } from 'react'
import VerifyEmailPage from '@/app/components/verify-email-page'

export default function VerifyEmail() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyEmailPage />
    </Suspense>
  )
}
