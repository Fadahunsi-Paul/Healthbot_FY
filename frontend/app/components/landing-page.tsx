"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  ChevronLeft,
  ChevronRight,
  Activity,
  Heart,
  Brain,
  Clock,
  BookOpen,
  User,
  Shield,
  Star,
  CheckCircle,
} from "lucide-react"

interface LandingPageProps {
  onNavigate: (page: "landing" | "signup" | "signin" | "chat") => void
}

const healthTips = [
  {
    icon: <Heart className="w-8 h-8 text-red-500" />,
    title: "Heart Health",
    tip: "Regular exercise for just 30 minutes a day can reduce your risk of heart disease by up to 35%.",
  },
  {
    icon: <Brain className="w-8 h-8 text-purple-500" />,
    title: "Mental Wellness",
    tip: "Practicing mindfulness and meditation can improve cognitive function and reduce stress levels.",
  },
  {
    icon: <Activity className="w-8 h-8 text-green-500" />,
    title: "Stay Active",
    tip: "Taking 10,000 steps daily can boost your immune system and improve overall health.",
  },
]

const whyUsFeatures = [
  {
    icon: <Clock className="w-12 h-12 text-blue-600" />,
    title: "24/7 Availability",
    description: "Get instant health guidance anytime, anywhere with our AI assistant.",
    benefits: ["Always accessible", "No appointment needed", "Instant responses", "Global availability"],
  },
  {
    icon: <BookOpen className="w-12 h-12 text-green-600" />,
    title: "Evidence-Based",
    description: "All responses based on current medical research and clinical guidelines.",
    benefits: ["Latest medical research", "Clinical guidelines", "Peer-reviewed sources", "Continuously updated"],
  },
  {
    icon: <User className="w-12 h-12 text-purple-600" />,
    title: "Personalized Care",
    description: "Tailored health recommendations based on your specific needs.",
    benefits: ["Individual health profile", "Custom recommendations", "Personal health history", "Adaptive learning"],
  },
]

export default function LandingPage({ onNavigate }: LandingPageProps) {
  const [currentTip, setCurrentTip] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % healthTips.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const nextTip = () => setCurrentTip((prev) => (prev + 1) % healthTips.length)
  const prevTip = () => setCurrentTip((prev) => (prev - 1 + healthTips.length) % healthTips.length)

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">HealthBot</span>
            </div>
            <div className="flex space-x-4">
              <Button variant="ghost" onClick={() => onNavigate("signin")}>
                Sign In
              </Button>
              <Button onClick={() => onNavigate("signup")}>Sign Up</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Your AI Health
            <span className="text-blue-600"> Companion</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Get instant medical insights, analyze health scans, and receive personalized health advice from our advanced
            AI chatbot powered by medical expertise.
          </p>
          <Button size="lg" className="text-lg px-8 py-3" onClick={() => onNavigate("signup")}>
            Try It Now
          </Button>
        </div>
      </section>

      {/* Why Us Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why Choose HealthBot?</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience the future of healthcare with our cutting-edge AI technology designed to provide you with the
              best possible health guidance.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {whyUsFeatures.map((feature, index) => (
              <Card
                key={index}
                className="bg-white shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border-0"
              >
                <CardContent className="p-8 text-center">
                  <div className="flex justify-center mb-6">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-full flex items-center justify-center">
                      {feature.icon}
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 text-lg mb-6 leading-relaxed">{feature.description}</p>

                  <div className="space-y-3">
                    {feature.benefits.map((benefit, benefitIndex) => (
                      <div key={benefitIndex} className="flex items-center justify-center space-x-2">
                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">{benefit}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Stats Section */}
          <div className="mt-16 bg-white rounded-2xl shadow-xl p-8">
            <div className="grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
                <div className="text-gray-600">Always Available</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-600 mb-2">10K+</div>
                <div className="text-gray-600">Medical Sources</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-purple-600 mb-2">99.9%</div>
                <div className="text-gray-600">Accuracy Rate</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-600 mb-2">50K+</div>
                <div className="text-gray-600">Happy Users</div>
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-12 text-center">
            <div className="flex justify-center items-center space-x-6 mb-6">
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-green-500" />
                <span className="text-gray-700 font-medium">HIPAA Compliant</span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="w-6 h-6 text-yellow-500" />
                <span className="text-gray-700 font-medium">FDA Guidelines</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-6 h-6 text-blue-500" />
                <span className="text-gray-700 font-medium">Clinically Validated</span>
              </div>
            </div>
            <p className="text-gray-500 text-sm">Trusted by healthcare professionals and patients worldwide</p>
          </div>
        </div>
      </section>

      {/* Health Tips Carousel */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Daily Health Tips</h2>
          <div className="relative">
            <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 shadow-lg border-0">
              <CardContent className="p-8">
                <div className="flex items-center justify-center mb-6">{healthTips[currentTip].icon}</div>
                <h3 className="text-2xl font-semibold text-center mb-4">{healthTips[currentTip].title}</h3>
                <p className="text-gray-600 text-center text-lg leading-relaxed">{healthTips[currentTip].tip}</p>
              </CardContent>
            </Card>
            <Button
              variant="outline"
              size="icon"
              className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white shadow-lg hover:shadow-xl"
              onClick={prevTip}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white shadow-lg hover:shadow-xl"
              onClick={nextTip}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex justify-center mt-6 space-x-2">
            {healthTips.map((_, index) => (
              <button
                key={index}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentTip ? "bg-blue-600" : "bg-gray-300"
                }`}
                onClick={() => setCurrentTip(index)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Medical Scan Samples */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">AI-Powered Medical Image Analysis</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="hover:shadow-lg transition-shadow bg-white">
              <CardContent className="p-6">
                <div className="aspect-square bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg mb-4 flex items-center justify-center">
                  <img
                    src="/placeholder.svg?height=200&width=200"
                    alt="Chest X-Ray Analysis"
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">X-Ray Analysis</h3>
                <p className="text-gray-600">Advanced AI detection for chest X-rays and bone fractures</p>
              </CardContent>
            </Card>
            <Card className="hover:shadow-lg transition-shadow bg-white">
              <CardContent className="p-6">
                <div className="aspect-square bg-gradient-to-br from-green-100 to-green-200 rounded-lg mb-4 flex items-center justify-center">
                  <img
                    src="/placeholder.svg?height=200&width=200"
                    alt="MRI Scan Analysis"
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">MRI Scanning</h3>
                <p className="text-gray-600">Detailed brain and organ analysis with AI insights</p>
              </CardContent>
            </Card>
            <Card className="hover:shadow-lg transition-shadow bg-white">
              <CardContent className="p-6">
                <div className="aspect-square bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg mb-4 flex items-center justify-center">
                  <img
                    src="/placeholder.svg?height=200&width=200"
                    alt="Skin Analysis"
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">Skin Analysis</h3>
                <p className="text-gray-600">Dermatological assessment and skin condition detection</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-700">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Transform Your Health Journey?</h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of users who trust HealthBot for reliable, personalized health guidance available 24/7.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              variant="secondary"
              className="text-lg px-8 py-4 bg-white text-blue-600 hover:bg-gray-100"
              onClick={() => onNavigate("signup")}
            >
              Get Started Free
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-blue-600 bg-transparent"
              onClick={() => onNavigate("signin")}
            >
              Sign In
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">HealthBot</span>
              </div>
              <p className="text-gray-400 mb-4">
                Your trusted AI health companion providing evidence-based medical guidance 24/7.
              </p>
              <div className="flex space-x-4">
                <div className="flex items-center space-x-2">
                  <Shield className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-gray-400">Secure & Private</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-blue-400" />
                  <span className="text-sm text-gray-400">Clinically Validated</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li>24/7 AI Assistant</li>
                <li>Medical Image Analysis</li>
                <li>Personalized Recommendations</li>
                <li>Health Tracking</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Help Center</li>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
                <li>Contact Us</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>
              &copy; 2024 HealthBot. All rights reserved. | Medical advice should not replace professional consultation.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
