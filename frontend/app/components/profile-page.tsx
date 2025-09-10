"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, Camera, User, Bell, Shield, Heart, Activity, CheckCircle, AlertCircle } from "lucide-react"
import { authAPI } from "@/app/utils/auth"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface ProfilePageProps {
  user: { name: string; email: string }
  onBack: () => void
  onUpdateProfile: (userData: any) => void
}

export default function ProfilePage({ user, onBack, onUpdateProfile }: ProfilePageProps) {
  const [profileData, setProfileData] = useState({
    fullName: user.name,
    email: user.email,
    phone: "",
    dateOfBirth: "",
    address: "",
    emergencyContact: "",
    medicalConditions: "",
    allergies: "",
    medications: "",
    bloodType: "",
    height: "",
    weight: "",
  })

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    pushNotifications: true,
    healthReminders: true,
    appointmentReminders: true,
  })

  const [privacy, setPrivacy] = useState({
    shareHealthData: false,
    allowAnalytics: true,
    publicProfile: false,
  })

  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Load complete profile data when component mounts
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        setIsLoadingProfile(true)
        const profileResponse = await authAPI.getProfile()
        const profile = profileResponse.profile || {}
        
        // Update state with loaded profile data
        setProfileData({
          fullName: user.name,
          email: user.email,
          phone: profile.phone || "",
          dateOfBirth: profile.date_of_birth || "",
          address: profile.address || "",
          emergencyContact: profile.emergency_contact || "",
          medicalConditions: profile.medical_conditions || "",
          allergies: profile.allergies || "",
          medications: profile.medications || "",
          bloodType: profile.blood_type || "",
          height: profile.height || "",
          weight: profile.weight || "",
        })

        setNotifications({
          emailNotifications: profile.email_notifications ?? true,
          pushNotifications: profile.push_notifications ?? true,
          healthReminders: profile.health_reminders ?? true,
          appointmentReminders: profile.appointment_reminders ?? true,
        })

        setPrivacy({
          shareHealthData: profile.share_health_data ?? false,
          allowAnalytics: profile.allow_analytics ?? true,
          publicProfile: profile.public_profile ?? false,
        })
        
      } catch (error) {
        console.error('Error loading profile:', error)
        // If profile doesn't exist, that's okay - use defaults
      } finally {
        setIsLoadingProfile(false)
      }
    }

    loadProfileData()
  }, [user])

  const handleSave = async () => {
    setIsLoading(true)
    setMessage(null)
    
    try {
      console.log('Starting profile save...')
      
      // Split full name into first and last name
      const nameParts = profileData.fullName.trim().split(' ')
      const firstName = nameParts[0] || ''
      const lastName = nameParts.slice(1).join(' ') || ''
      
      // Prepare complete profile data
      const completeProfileData = {
        // Basic user fields
        first_name: firstName,
        last_name: lastName,
        email: profileData.email,
        
        // Extended profile fields - handle empty strings properly
        phone: profileData.phone.trim() || null,
        date_of_birth: profileData.dateOfBirth.trim() || null,
        address: profileData.address.trim() || null,
        emergency_contact: profileData.emergencyContact.trim() || null,
        medical_conditions: profileData.medicalConditions.trim() || null,
        allergies: profileData.allergies.trim() || null,
        medications: profileData.medications.trim() || null,
        blood_type: profileData.bloodType.trim() || null,
        height: profileData.height.trim() || null,
        weight: profileData.weight.trim() || null,
        
        // Notification settings
        email_notifications: notifications.emailNotifications,
        push_notifications: notifications.pushNotifications,
        health_reminders: notifications.healthReminders,
        appointment_reminders: notifications.appointmentReminders,
        
        // Privacy settings
        share_health_data: privacy.shareHealthData,
        allow_analytics: privacy.allowAnalytics,
        public_profile: privacy.publicProfile,
      }
      
      console.log('Complete profile data to save:', completeProfileData)
      
      // Update user profile in backend
      console.log('Calling authAPI.updateProfile...')
      const response = await authAPI.updateProfile(completeProfileData)
      
      console.log('Profile update response:', response)
      
      // Extract user data from response
      const updatedUser = response.user
      
      // Update the parent component with new user data
      const updatedAppUser = {
        name: `${updatedUser.first_name} ${updatedUser.last_name}`.trim(),
        email: updatedUser.email
      }
      
      console.log('Updating parent with:', updatedAppUser)
      onUpdateProfile(updatedAppUser)
      
      setMessage({ type: 'success', text: 'Profile updated successfully! Changes have been saved.' })
      
      // Navigate back after a delay to show success message
      setTimeout(() => {
        onBack()
      }, 2000)
      
      console.log('Profile save completed successfully')
      
    } catch (error: any) {
      console.error('Profile update error:', error)
      setMessage({ 
        type: 'error', 
        text: error.message || 'Failed to update profile. Please try again.' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getUserInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  if (isLoadingProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center">
          <Button variant="ghost" size="icon" onClick={onBack} className="mr-4">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Overview */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardContent className="p-6 text-center">
                <div className="relative inline-block mb-4">
                  <Avatar className="w-24 h-24">
                    <AvatarFallback className="bg-blue-600 text-white text-2xl">
                      {getUserInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                  <Button
                    size="icon"
                    className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Camera className="w-4 h-4" />
                  </Button>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-1">{user.name}</h2>
                <p className="text-gray-600 mb-4">{user.email}</p>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center justify-center space-x-2">
                    <Heart className="w-4 h-4 text-red-500" />
                    <span>Health Score: 85%</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2">
                    <Activity className="w-4 h-4 text-green-500" />
                    <span>Active Member</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings Forms */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span>Personal Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={profileData.fullName}
                      onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                  <div>
                    <Label htmlFor="dateOfBirth">Date of Birth</Label>
                    <Input
                      id="dateOfBirth"
                      type="date"
                      value={profileData.dateOfBirth}
                      onChange={(e) => setProfileData({ ...profileData, dateOfBirth: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={profileData.address}
                    onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                    placeholder="123 Main St, City, State 12345"
                  />
                </div>

                <div>
                  <Label htmlFor="emergencyContact">Emergency Contact</Label>
                  <Input
                    id="emergencyContact"
                    value={profileData.emergencyContact}
                    onChange={(e) => setProfileData({ ...profileData, emergencyContact: e.target.value })}
                    placeholder="Name and phone number"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Health Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Heart className="w-5 h-5" />
                  <span>Health Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="bloodType">Blood Type</Label>
                    <Select
                      value={profileData.bloodType}
                      onValueChange={(value) => setProfileData({ ...profileData, bloodType: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select blood type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="A+">A+</SelectItem>
                        <SelectItem value="A-">A-</SelectItem>
                        <SelectItem value="B+">B+</SelectItem>
                        <SelectItem value="B-">B-</SelectItem>
                        <SelectItem value="AB+">AB+</SelectItem>
                        <SelectItem value="AB-">AB-</SelectItem>
                        <SelectItem value="O+">O+</SelectItem>
                        <SelectItem value="O-">O-</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="height">Height (cm)</Label>
                    <Input
                      id="height"
                      value={profileData.height}
                      onChange={(e) => setProfileData({ ...profileData, height: e.target.value })}
                      placeholder="170"
                    />
                  </div>
                  <div>
                    <Label htmlFor="weight">Weight (kg)</Label>
                    <Input
                      id="weight"
                      value={profileData.weight}
                      onChange={(e) => setProfileData({ ...profileData, weight: e.target.value })}
                      placeholder="70"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="medicalConditions">Medical Conditions</Label>
                  <Textarea
                    id="medicalConditions"
                    value={profileData.medicalConditions}
                    onChange={(e) => setProfileData({ ...profileData, medicalConditions: e.target.value })}
                    placeholder="List any chronic conditions, past surgeries, etc."
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="allergies">Allergies</Label>
                  <Textarea
                    id="allergies"
                    value={profileData.allergies}
                    onChange={(e) => setProfileData({ ...profileData, allergies: e.target.value })}
                    placeholder="Food allergies, drug allergies, environmental allergies"
                    rows={2}
                  />
                </div>

                <div>
                  <Label htmlFor="medications">Current Medications</Label>
                  <Textarea
                    id="medications"
                    value={profileData.medications}
                    onChange={(e) => setProfileData({ ...profileData, medications: e.target.value })}
                    placeholder="List current medications and dosages"
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="w-5 h-5" />
                  <span>Notification Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="emailNotifications">Email Notifications</Label>
                    <p className="text-sm text-gray-600">Receive health tips and updates via email</p>
                  </div>
                  <Switch
                    id="emailNotifications"
                    checked={notifications.emailNotifications}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, emailNotifications: checked })}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="pushNotifications">Push Notifications</Label>
                    <p className="text-sm text-gray-600">Get instant notifications on your device</p>
                  </div>
                  <Switch
                    id="pushNotifications"
                    checked={notifications.pushNotifications}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, pushNotifications: checked })}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="healthReminders">Health Reminders</Label>
                    <p className="text-sm text-gray-600">Reminders for medication and checkups</p>
                  </div>
                  <Switch
                    id="healthReminders"
                    checked={notifications.healthReminders}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, healthReminders: checked })}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="appointmentReminders">Appointment Reminders</Label>
                    <p className="text-sm text-gray-600">Get notified about upcoming appointments</p>
                  </div>
                  <Switch
                    id="appointmentReminders"
                    checked={notifications.appointmentReminders}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, appointmentReminders: checked })}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Privacy Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span>Privacy & Security</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="shareHealthData">Share Health Data</Label>
                    <p className="text-sm text-gray-600">Allow sharing anonymized data for research</p>
                  </div>
                  <Switch
                    id="shareHealthData"
                    checked={privacy.shareHealthData}
                    onCheckedChange={(checked) => setPrivacy({ ...privacy, shareHealthData: checked })}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="allowAnalytics">Analytics</Label>
                    <p className="text-sm text-gray-600">Help improve our service with usage analytics</p>
                  </div>
                  <Switch
                    id="allowAnalytics"
                    checked={privacy.allowAnalytics}
                    onCheckedChange={(checked) => setPrivacy({ ...privacy, allowAnalytics: checked })}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="publicProfile">Public Profile</Label>
                    <p className="text-sm text-gray-600">Make your profile visible to other users</p>
                  </div>
                  <Switch
                    id="publicProfile"
                    checked={privacy.publicProfile}
                    onCheckedChange={(checked) => setPrivacy({ ...privacy, publicProfile: checked })}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Status Message */}
            {message && (
              <Alert className={message.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                {message.type === 'success' ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-600" />
                )}
                <AlertDescription className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
                  {message.text}
                </AlertDescription>
              </Alert>
            )}

            {/* Save Button */}
            <div className="flex justify-end space-x-4">
              <Button variant="outline" onClick={onBack} disabled={isLoading}>
                Cancel
              </Button>
              <Button 
                onClick={handleSave} 
                className="bg-blue-600 hover:bg-blue-700" 
                disabled={isLoading}
              >
                {isLoading ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
