"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ForecastField, ForecastGrid } from "./forecast-field"

interface ForecastData {
  id: string
  label: string
  value: number
  isEditable: boolean
  error?: string
}

export default function ForecastExample() {
  const [forecasts, setForecasts] = useState<ForecastData[]>([
    {
      id: "revenue",
      label: "Revenue Forecast",
      value: 35177,
      isEditable: true,
    },
    {
      id: "expenses",
      label: "Expenses Forecast", 
      value: 35177,
      isEditable: true,
    },
    {
      id: "net_profit",
      label: "Net Profit",
      value: 12628798734,
      isEditable: false, // This will be calculated
    },
    {
      id: "growth_rate",
      label: "Growth Rate (%)",
      value: 15000,
      isEditable: true,
    },
  ])

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  const handleForecastChange = (id: string, value: number) => {
    setForecasts(prev => prev.map(forecast => 
      forecast.id === id ? { ...forecast, value } : forecast
    ))

    // Clear validation error when user starts typing
    if (validationErrors[id]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[id]
        return newErrors
      })
    }

    // Auto-calculate dependent fields
    if (id === "revenue" || id === "expenses") {
      const revenue = id === "revenue" ? value : forecasts.find(f => f.id === "revenue")?.value || 0
      const expenses = id === "expenses" ? value : forecasts.find(f => f.id === "expenses")?.value || 0
      const netProfit = revenue - expenses

      setForecasts(prev => prev.map(forecast => 
        forecast.id === "net_profit" ? { ...forecast, value: netProfit } : forecast
      ))
    }
  }

  const validateForecasts = () => {
    const errors: Record<string, string> = {}

    forecasts.forEach(forecast => {
      if (forecast.isEditable) {
        if (forecast.value < 0) {
          errors[forecast.id] = "Value cannot be negative"
        } else if (forecast.value === 0) {
          errors[forecast.id] = "Value must be greater than zero"
        } else if (forecast.id === "growth_rate" && forecast.value > 1000) {
          errors[forecast.id] = "Growth rate seems too high (max 1000%)"
        }
      }
    })

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSave = () => {
    if (validateForecasts()) {
      console.log("Saving forecasts:", forecasts)
      // Here you would typically save to your backend
      alert("Forecasts saved successfully!")
    } else {
      console.log("Validation errors:", validationErrors)
    }
  }

  const resetToDefaults = () => {
    setForecasts([
      {
        id: "revenue",
        label: "Revenue Forecast",
        value: 35177,
        isEditable: true,
      },
      {
        id: "expenses",
        label: "Expenses Forecast", 
        value: 35177,
        isEditable: true,
      },
      {
        id: "net_profit",
        label: "Net Profit",
        value: 0,
        isEditable: false,
      },
      {
        id: "growth_rate",
        label: "Growth Rate (%)",
        value: 15000,
        isEditable: true,
      },
    ])
    setValidationErrors({})
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Forecast Management System
          </CardTitle>
          <p className="text-gray-600">
            Editable fields allow user input, while calculated fields are automatically computed.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Individual Forecast Fields */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Individual Forecast Fields</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium text-gray-700">Editable Fields</h4>
                
                <ForecastField
                  label="Revenue Forecast"
                  value={forecasts.find(f => f.id === "revenue")?.value || 0}
                  onChange={(value) => handleForecastChange("revenue", value)}
                  isEditable={true}
                  placeholder="Enter revenue forecast"
                  error={validationErrors.revenue}
                />
                
                <ForecastField
                  label="Expenses Forecast"
                  value={forecasts.find(f => f.id === "expenses")?.value || 0}
                  onChange={(value) => handleForecastChange("expenses", value)}
                  isEditable={true}
                  placeholder="Enter expenses forecast"
                  error={validationErrors.expenses}
                />
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium text-gray-700">Calculated Fields</h4>
                
                <ForecastField
                  label="Net Profit (Calculated)"
                  value={forecasts.find(f => f.id === "net_profit")?.value || 0}
                  isEditable={false}
                />
                
                <ForecastField
                  label="Growth Rate"
                  value={forecasts.find(f => f.id === "growth_rate")?.value || 0}
                  onChange={(value) => handleForecastChange("growth_rate", value)}
                  isEditable={true}
                  placeholder="Enter growth rate %"
                  error={validationErrors.growth_rate}
                />
              </div>
            </div>
          </div>

          {/* Forecast Grid */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Forecast Grid Layout</h3>
            
            <Card className="bg-gray-50">
              <CardContent className="p-6">
                <ForecastGrid
                  forecasts={forecasts.map(forecast => ({
                    ...forecast,
                    onChange: handleForecastChange,
                    error: validationErrors[forecast.id]
                  }))}
                />
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t">
            <Button onClick={handleSave} className="flex-1 sm:flex-none">
              Save Forecasts
            </Button>
            <Button 
              onClick={resetToDefaults} 
              variant="outline" 
              className="flex-1 sm:flex-none"
            >
              Reset to Defaults
            </Button>
          </div>

          {/* Current Values Display */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Current Forecast Values:</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              {forecasts.map(forecast => (
                <div key={forecast.id} className="flex justify-between">
                  <span className="text-blue-800">{forecast.label}:</span>
                  <span className="font-mono text-blue-900">
                    {forecast.value.toLocaleString()}
                    {!forecast.isEditable && <span className="text-blue-600 ml-1">(calculated)</span>}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
