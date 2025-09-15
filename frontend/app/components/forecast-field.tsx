"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface ForecastFieldProps {
  value: number
  onChange?: (value: number) => void
  isEditable?: boolean
  placeholder?: string
  className?: string
  label?: string
  disabled?: boolean
  error?: string
  onBlur?: () => void
  onFocus?: () => void
}

export default function ForecastField({
  value,
  onChange,
  isEditable = true,
  placeholder = "Enter value",
  className,
  label,
  disabled = false,
  error,
  onBlur,
  onFocus,
}: ForecastFieldProps) {
  const [displayValue, setDisplayValue] = useState("")
  const [isFocused, setIsFocused] = useState(false)

  // Format number with commas
  const formatNumber = (num: number): string => {
    return num.toLocaleString('en-US')
  }

  // Parse formatted string back to number
  const parseNumber = (str: string): number => {
    const cleaned = str.replace(/,/g, '')
    const parsed = parseFloat(cleaned)
    return isNaN(parsed) ? 0 : parsed
  }

  // Update display value when prop value changes
  useEffect(() => {
    setDisplayValue(formatNumber(value))
  }, [value])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    
    // Allow only numbers, commas, and decimal points
    const sanitizedValue = inputValue.replace(/[^0-9.,]/g, '')
    
    setDisplayValue(sanitizedValue)
    
    // Parse and call onChange
    const numericValue = parseNumber(sanitizedValue)
    if (onChange && numericValue !== value) {
      onChange(numericValue)
    }
  }

  const handleFocus = () => {
    setIsFocused(true)
    onFocus?.()
  }

  const handleBlur = () => {
    setIsFocused(false)
    // Format the value properly on blur
    setDisplayValue(formatNumber(value))
    onBlur?.()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    // Allow: backspace, delete, tab, escape, enter, decimal point, comma
    if ([8, 9, 27, 13, 46, 110, 190, 188].indexOf(e.keyCode) !== -1 ||
        // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        (e.keyCode === 65 && e.ctrlKey === true) ||
        (e.keyCode === 67 && e.ctrlKey === true) ||
        (e.keyCode === 86 && e.ctrlKey === true) ||
        (e.keyCode === 88 && e.ctrlKey === true) ||
        // Allow: home, end, left, right, down, up
        (e.keyCode >= 35 && e.keyCode <= 40)) {
      return
    }
    // Ensure that it is a number and stop the keypress
    if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
      e.preventDefault()
    }
  }

  return (
    <div className={cn("w-full", className)}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      
      {isEditable && !disabled ? (
        <Input
          type="text"
          value={displayValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyPress}
          placeholder={placeholder}
          className={cn(
            "text-right font-mono",
            "border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            error && "border-red-500 focus:border-red-500 focus:ring-red-500",
            className
          )}
          aria-invalid={!!error}
        />
      ) : (
        <div
          className={cn(
            "px-3 py-2 text-right font-mono text-gray-900 bg-gray-50 border border-gray-300 rounded-md",
            "min-h-[36px] flex items-center justify-end",
            disabled && "opacity-60",
            className
          )}
          title={disabled ? "This value is calculated automatically" : "This value is not editable"}
        >
          {formatNumber(value)}
        </div>
      )}
      
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}

// Forecast Grid Component for multiple forecast fields
interface ForecastGridProps {
  forecasts: Array<{
    id: string
    label: string
    value: number
    isEditable: boolean
    onChange?: (id: string, value: number) => void
    error?: string
  }>
  className?: string
}

export function ForecastGrid({ forecasts, className }: ForecastGridProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {forecasts.map((forecast) => (
        <div key={forecast.id} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
          <div className="sm:col-span-1">
            <label className="block text-sm font-medium text-gray-700">
              {forecast.label}
            </label>
          </div>
          <div className="sm:col-span-2">
            <ForecastField
              value={forecast.value}
              onChange={forecast.onChange ? (value) => forecast.onChange!(forecast.id, value) : undefined}
              isEditable={forecast.isEditable}
              error={forecast.error}
              placeholder={`Enter ${forecast.label.toLowerCase()}`}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
