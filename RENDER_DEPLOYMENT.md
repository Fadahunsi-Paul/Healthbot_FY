# Render Deployment Guide for Healthbot

This guide will help you deploy your Django healthbot application to Render.

## Prerequisites

1. A GitHub repository with your code
2. A Render account (sign up at render.com)

## Deployment Steps

### 1. Connect Repository to Render

1. Go to your Render dashboard
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file

### 2. Environment Variables Setup

In your Render dashboard, set these environment variables for your web service:

**Required:**
- `EMAIL_HOST_USER`: Your Gmail address for sending emails
- `EMAIL_HOST_PASSWORD`: Your Gmail app password (not your regular password)

**Optional (for custom domains):**
- `ALLOWED_HOSTS`: Add your custom domain if you have one
- `SITE_URL`: Update with your actual domain

### 3. Frontend Configuration

After deploying the backend:

1. Update your frontend's API configuration to point to your Render backend URL
2. Update the CORS settings in `backend/settings.py` to include your frontend URL
3. Deploy your Next.js frontend to Render or Vercel

### 4. Database Setup

The render.yaml includes a PostgreSQL database. After deployment:

1. Run migrations manually if needed:
   ```bash
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

### 5. Services Overview

Your deployment includes:

- **Web Service**: Main Django API
- **Redis Service**: For Celery task queue
- **PostgreSQL Database**: For persistent data storage
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task execution (daily health tips, cleanup)

### 6. Monitoring

- Check logs in the Render dashboard for each service
- Monitor Redis and PostgreSQL usage
- Set up alerts for service failures

### 7. Custom Domain (Optional)

1. In Render dashboard, go to your web service
2. Add your custom domain
3. Update CORS settings accordingly
4. Update environment variables

## Troubleshooting

### Common Issues:

1. **Build Failures**: Check that all dependencies are in requirements.txt
2. **Database Connection**: Ensure DATABASE_URL is set correctly
3. **Celery Issues**: Check Redis connection string
4. **CORS Errors**: Update CORS_ALLOWED_ORIGINS with your frontend URL

### Logs:

Check logs in Render dashboard:
- Web service logs
- Worker service logs
- Beat service logs

## Cost Optimization

- Start with "Starter" plans for all services
- Upgrade to "Standard" or "Pro" as needed
- Monitor usage in Render dashboard
- Consider pausing services during development

## Security Notes

- Never commit secrets to git
- Use Render's environment variables for sensitive data
- Enable HTTPS (automatic on Render)
- Keep dependencies updated
