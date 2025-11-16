# Feedback Storage Directory

This directory stores user feedback submitted through the Steam Insights Dashboard.

## Structure

- **feedback_YYYYMMDD_HHMMSS.json** - JSON files containing feedback metadata
- **screenshot_YYYYMMDD_HHMMSS.png** - Screenshot images attached to feedback

## Feedback JSON Format

```json
{
  "timestamp": "2025-11-16T12:30:45.123456",
  "page": "💡 Concept & Research",
  "feedback": "User feedback text here...",
  "screenshot": "screenshot_20251116_123045.png",
  "email": "user@example.com"
}
```

## Accessing Feedback

Users can submit feedback via:
1. The **💬 Feedback** button in the top-right corner of any page
2. The **💬 Feedback Management** page in Data Management stage (admin view)

## Privacy Note

- Email addresses are optional
- Screenshots may contain sensitive data - handle appropriately
- Review and delete old feedback regularly
