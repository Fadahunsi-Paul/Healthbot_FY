"use client"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, Square, Upload, RefreshCw, Play, Pause, X } from "lucide-react"
import { chatAPI, isAuthenticated } from "@/app/utils/auth"

interface AudioRecordProps {
  sessionId?: string | null
  onUploaded?: (result: { session_id: number; transcript: string; label: string; answer: string }) => void
  onCancel?: () => void
}

export default function AudioRecord({ sessionId, onUploaded, onCancel }: AudioRecordProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    return () => {
      // Cleanup tracks
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop())
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      setError(null)
      if (!isAuthenticated()) {
        setError("Please sign in to record audio.")
        return
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream
      const recorder = new MediaRecorder(stream)
      audioChunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) audioChunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" })
        setAudioBlob(blob)
      }
      recorder.start()
      mediaRecorderRef.current = recorder
      setIsRecording(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start recording")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop()
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop())
      setIsRecording(false)
    }
  }

  const resetRecording = () => {
    setAudioBlob(null)
    setIsPlaying(false)
    setError(null)
  }

  const togglePlayback = () => {
    const el = audioRef.current
    if (!el) return
    if (isPlaying) {
      el.pause()
      setIsPlaying(false)
    } else {
      el.play()
      setIsPlaying(true)
    }
  }

  const handleUpload = async () => {
    if (!audioBlob) return
    try {
      setIsUploading(true)
      setError(null)
      // Convert blob to File so the backend gets a filename/extension
      const file = new File([audioBlob], "recording.webm", { type: audioBlob.type || "audio/webm" })
      const result = await chatAPI.uploadAudio(file, sessionId || undefined)
      onUploaded?.(result)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to upload audio")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Card className="w-full">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Audio Input</h3>
          {onCancel && (
            <Button size="icon" variant="ghost" onClick={onCancel} aria-label="Close">
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {!isRecording ? (
            <Button onClick={startRecording} disabled={!!audioBlob}>
              <Mic className="w-4 h-4 mr-2" /> Start Recording
            </Button>
          ) : (
            <Button variant="destructive" onClick={stopRecording}>
              <Square className="w-4 h-4 mr-2" /> Stop
            </Button>
          )}

          <Button variant="outline" onClick={resetRecording} disabled={!audioBlob || isRecording}>
            <RefreshCw className="w-4 h-4 mr-2" /> Reset
          </Button>

          <Button onClick={togglePlayback} disabled={!audioBlob} variant="secondary">
            {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />} {isPlaying ? "Pause" : "Play"}
          </Button>

          <Button onClick={handleUpload} disabled={!audioBlob || isUploading}>
            <Upload className="w-4 h-4 mr-2" /> {isUploading ? "Uploading..." : "Upload"}
          </Button>
        </div>

        {/* Preview */}
        {audioBlob && (
          <audio
            ref={audioRef}
            src={URL.createObjectURL(audioBlob)}
            onEnded={() => setIsPlaying(false)}
            className="w-full"
            controls
          />
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}
      </CardContent>
    </Card>
  )
}


