"use client"

import { Activity } from "lucide-react"

export default function TypingIndicator() {
  return (
    <div className="flex items-start space-x-2 max-w-xs lg:max-w-md">
      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
        <Activity className="w-4 h-4 text-white" />
      </div>
      <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
        <div className="flex items-center space-x-1">
          <span className="text-sm text-gray-600">AI is thinking</span>
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}
