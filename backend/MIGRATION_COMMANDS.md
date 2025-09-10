# Database Migration Commands

To apply the new UserProfile model changes, run these commands:

```bash
# Navigate to backend directory
cd backend

# Create migrations for the new UserProfile model
python manage.py makemigrations auths

# Apply the migrations to the database
python manage.py migrate

# (Optional) Create a superuser if you haven't already
python manage.py createsuperuser
```

## What was added:

1. **UserProfile Model**: Stores extended profile information including:
   - Personal info (phone, date of birth, address, emergency contact)
   - Health info (medical conditions, allergies, medications, blood type, height, weight)
   - Notification settings
   - Privacy settings

2. **Enhanced API**: The `/auth/profile/` endpoint now:
   - Accepts GET requests to retrieve complete profile data
   - Accepts PUT requests to update all profile fields
   - Automatically creates UserProfile if it doesn't exist

3. **Frontend Integration**: Profile page now:
   - Loads existing profile data on mount
   - Saves all fields to backend
   - Shows loading states during operations
