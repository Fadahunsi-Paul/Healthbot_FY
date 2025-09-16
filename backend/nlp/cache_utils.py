# nlp/cache_utils.py
from django.utils import timezone
from datetime import timedelta
from nlp.models import CachedAnswer

DEFAULT_TTL_DAYS = 7

def get_cached_answer(query_text: str):
    try:
        entry = CachedAnswer.objects.get(query_text=query_text)
        if entry.expires_at > timezone.now():
            return entry.answer
        entry.delete()
    except CachedAnswer.DoesNotExist:
        return None
    return None

def set_cached_answer(query_text: str, answer: str, ttl_days: int = DEFAULT_TTL_DAYS):
    expires_at = timezone.now() + timedelta(days=ttl_days)
    CachedAnswer.objects.update_or_create(
        query_text=query_text,
        defaults={"answer": answer, "expires_at": expires_at}
    )

def clear_expired_cache():
    now = timezone.now()
    CachedAnswer.objects.filter(expires_at__lte=now).delete()
