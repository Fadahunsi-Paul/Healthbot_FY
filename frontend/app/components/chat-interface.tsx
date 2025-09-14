"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Send, Mic, Paperclip, Activity, ChevronDown, MessageSquare, User, LogOut, Trash2, Menu, X } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import TypingIndicator from "./typing-indicator"
import { chatAPI, isAuthenticated } from "@/app/utils/auth"
import AudioRecord from "./audio-record"

interface ChatInterfaceProps {
  user: { name: string; email: string }
  onSignOut: () => void
  onNavigate: (page: "landing" | "signup" | "signin" | "chat" | "profile") => void
}

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
}

interface ChatSession {
  id: number
  title: string
  created_at: string
}

interface ChatMessage {
  sender: string
  message: string
  timestamp: string
}

export default function ChatInterface({ user, onSignOut, onNavigate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI health assistant. How can I help you today?",
      sender: "ai",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoadingSessions, setIsLoadingSessions] = useState(true)
  const [showAudioInput, setShowAudioInput] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const SESSION_STORAGE_KEY = "current_chat_session_id"

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // Load chat sessions on component mount
  useEffect(() => {
    loadChatSessions()
  }, [])

  // Auto-load last session history on mount (if available)
  useEffect(() => {
    const savedId = localStorage.getItem(SESSION_STORAGE_KEY)
    if (savedId && isAuthenticated()) {
      loadChatHistory(savedId).catch(() => {
        localStorage.removeItem(SESSION_STORAGE_KEY)
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Persist current session id changes
  useEffect(() => {
    if (currentSessionId) {
      localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId)
    } else {
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }, [currentSessionId])

  const loadChatSessions = async () => {
    try {
      setIsLoadingSessions(true)
      if (!isAuthenticated()) {
        console.error('User not authenticated')
        return
      }
      const sessions = await chatAPI.getChatSessions()
      setChatSessions(sessions)
    } catch (error) {
      console.error('Error loading chat sessions:', error)
      if (error instanceof Error && error.message === 'Authentication expired') {
        onSignOut() // Redirect to login
      }
    } finally {
      setIsLoadingSessions(false)
    }
  }

  const loadChatHistory = async (sessionId: string) => {
    try {
      if (!isAuthenticated()) {
        console.error('User not authenticated')
        return
      }
      const history = await chatAPI.getChatHistory(sessionId)
      const formattedMessages: Message[] = history.map((msg: ChatMessage, index: number) => ({
        id: index.toString(),
        content: msg.message,
        sender: msg.sender === 'bot' ? 'ai' : msg.sender as 'user' | 'ai',
        timestamp: new Date(msg.timestamp),
      }))
      setMessages(formattedMessages)
      setCurrentSessionId(sessionId)
    } catch (error) {
      console.error('Error loading chat history:', error)
      if (error instanceof Error && error.message === 'Authentication expired') {
        onSignOut() // Redirect to login
      }
    }
  }

  const startNewConversation = () => {
    setMessages([
      {
        id: "1",
        content: "Hello! I'm your AI health assistant. How can I help you today?",
        sender: "ai",
        timestamp: new Date(),
      },
    ])
    setCurrentSessionId(null)
  }

  const deleteSession = async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation() // Prevent triggering the card click
    
    if (!confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return
    }

    try {
      await chatAPI.deleteSession(sessionId)
      
      // Remove session from local state
      setChatSessions(prev => prev.filter(session => session.id.toString() !== sessionId))
      
      // If this was the current session, start a new conversation
      if (currentSessionId === sessionId) {
        startNewConversation()
      }
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Failed to delete the conversation. Please try again.')
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, newMessage])
    const messageToSend = inputMessage
    setInputMessage("")
    setIsTyping(true)

    try {
      if (!isAuthenticated()) {
        throw new Error('User not authenticated')
      }
      
      // Call the backend API with session support
      const data = await chatAPI.sendMessage(messageToSend, currentSessionId || undefined)
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: data.answer || "I'm sorry, I couldn't process your question at the moment. Please try again.",
        sender: "ai",
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, aiResponse])
      
      // Update current session ID if this was a new conversation
      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id.toString())
        // Reload sessions to get the updated list
        loadChatSessions()
      }
    } catch (error: unknown) {
      console.error('Error calling chatbot API:', error)
      
      let errorMessage = "I'm sorry, I'm having trouble connecting to the server. Please check your connection and try again."
      
      if (error instanceof Error && (error.message === 'Authentication expired' || error.message === 'User not authenticated')) {
        errorMessage = "Your session has expired. Please sign in again."
        onSignOut() // Redirect to login
      }
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessage,
        sender: "ai",
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, errorResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const getUserInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const handleAudioUploaded = (data: { session_id: number; transcript: string; label: string; answer: string }) => {
    const userTranscript: Message = {
      id: (Date.now()).toString(),
      content: data.transcript,
      sender: "user",
      timestamp: new Date(),
    }
    const aiReply: Message = {
      id: (Date.now() + 1).toString(),
      content: data.answer || "I'm sorry, I couldn't process your audio at the moment.",
      sender: "ai",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userTranscript, aiReply])

    if (!currentSessionId && data.session_id) {
      setCurrentSessionId(data.session_id.toString())
      loadChatSessions()
    }

    setShowAudioInput(false)
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const closeSidebar = () => {
    setSidebarOpen(false)
  }

  const handleSessionSelect = (sessionId: string) => {
    loadChatHistory(sessionId)
    // Close sidebar on mobile after selecting a session
    if (window.innerWidth < 768) {
      closeSidebar()
    }
  }

  return (
    <div className="h-screen flex bg-gray-50 relative">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:relative z-50 md:z-auto
        w-80 bg-white border-r border-gray-200 flex flex-col
        h-full
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0
      `}>
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">HealthBot</span>
            </div>
            {/* Close button for mobile */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={closeSidebar}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
          <Button className="w-full bg-transparent" variant="outline" onClick={startNewConversation}>
            <MessageSquare className="w-4 h-4 mr-2" />
            New Conversation
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Recent Conversations</h3>
          <div className="space-y-2">
            {isLoadingSessions ? (
              <div className="text-center text-gray-500 text-sm">Loading sessions...</div>
            ) : chatSessions.length === 0 ? (
              <div className="text-center text-gray-500 text-sm">No conversations yet</div>
            ) : (
              chatSessions.map((session) => (
                <Card 
                  key={session.id} 
                  className={`cursor-pointer hover:bg-gray-50 transition-colors ${
                    currentSessionId === session.id.toString() ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => handleSessionSelect(session.id.toString())}
                >
                  <CardContent className="p-3 relative group">
                    <h4 className="font-medium text-sm text-gray-900 mb-1 pr-8">{session.title}</h4>
                    <p className="text-xs text-gray-400 mt-1">{new Date(session.created_at).toLocaleDateString()}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6 hover:bg-red-100 hover:text-red-600"
                      onClick={(e) => deleteSession(session.id.toString(), e)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col w-full md:w-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            {/* Hamburger Menu Button for Mobile */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden mr-2"
              onClick={toggleSidebar}
            >
              <Menu className="w-5 h-5" />
            </Button>
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AI Health Assistant</h1>
              <p className="text-sm text-green-500">Online</p>
            </div>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center space-x-2">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-blue-600 text-white text-sm">
                    {getUserInitials(user.name)}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden md:block">{user.name}</span>
                <ChevronDown className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem disabled>
                <div className="flex flex-col">
                  <span className="font-medium">{user.name}</span>
                  <span className="text-sm text-gray-500">{user.email}</span>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onNavigate("profile")} className="flex items-center space-x-2">
                <User className="w-4 h-4" />
                <span>Profile Settings</span>
              </DropdownMenuItem>
              <Separator />
              <DropdownMenuItem onClick={onSignOut} className="text-red-600 flex items-center space-x-2">
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-2 xs:p-3 sm:p-4 space-y-4">
          {showAudioInput && (
            <div>
              <AudioRecord
                sessionId={currentSessionId}
                onUploaded={handleAudioUploaded}
                onCancel={() => setShowAudioInput(false)}
              />
            </div>
          )}
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`flex items-start space-x-2 max-w-[280px] xs:max-w-[320px] sm:max-w-xs md:max-w-sm lg:max-w-md xl:max-w-lg 2xl:max-w-xl`}>
                {message.sender === "ai" && (
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Activity className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`px-3 xs:px-4 py-2 rounded-lg ${
                    message.sender === "user" ? "bg-blue-600 text-white" : "bg-white border border-gray-200"
                  }`}
                >
                  <p className="text-sm break-words">{message.content}</p>
                  <p className={`text-xs mt-1 ${message.sender === "user" ? "text-blue-100" : "text-gray-500"}`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>

                {message.sender === "user" && (
                  <Avatar className="w-8 h-8 flex-shrink-0">
                    <AvatarFallback className="bg-gray-600 text-white text-xs">
                      {getUserInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <TypingIndicator />
            </div>
          )}
          
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-2 xs:p-3 sm:p-4">
          <div className="flex items-center space-x-1 xs:space-x-2">
            <Button variant="outline" size="icon" className="hidden xs:flex">
              <Paperclip className="w-4 h-4" />
            </Button>
            <div className="flex-1 relative">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your health question..."
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                className="pr-12 text-sm xs:text-base"
                disabled={isTyping}
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 transform -translate-y-1/2"
                onClick={() => setShowAudioInput((prev) => !prev)}
                aria-label="Toggle audio input"
              >
                <Mic className="w-4 h-4" />
              </Button>
            </div>
            <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isTyping} size="icon">
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center hidden xs:block">
            This AI assistant provides general health information and should not replace professional medical advice.
          </p>
        </div>
      </div>
    </div>
  )
}
