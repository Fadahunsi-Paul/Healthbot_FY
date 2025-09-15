from django.utils import timezone
from api.models import CachedAnswer

def get_cached_answer(query_text: str):
    """Check DB cache for valid entry (not expired)."""
    try:
        entry = CachedAnswer.objects.get(query_text=query_text)
        if entry.expires_at > timezone.now():
            return entry.answer
        else:
            entry.delete()  # expired, remove
    except CachedAnswer.DoesNotExist:
        return None
    return None

def set_cached_answer(query_text: str, answer: str, ttl_days: int = 7):
    """Store query-answer in DB with TTL."""
    expires_at = timezone.now() + timedelta(days=ttl_days)
    CachedAnswer.objects.update_or_create(
        query_text=query_text,
        defaults={"answer": answer, "expires_at": expires_at}
    )
