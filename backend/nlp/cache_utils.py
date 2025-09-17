# nlp/cache_utils.py
import hashlib
import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from nlp.models import CachedAnswer

DEFAULT_TTL_DAYS = 7


def _safe_mtime(path: str) -> str:
    try:
        return str(int(os.path.getmtime(path)))
    except Exception:
        return "0"


def _compute_cache_namespace() -> str:
    """Create a cache namespace from model/data mtimes so retrains invalidate cache.

    Uses modification times of train.csv, svm_model.pkl, tfidf_vectorizer.pkl.
    """
    base = settings.BASE_DIR
    train_csv = os.path.join(base, "api", "dataset", "train.csv")
    svm_pkl = os.path.join(base, "api", "svm_model.pkl")
    tfidf_pkl = os.path.join(base, "api", "tfidf_vectorizer.pkl")

    stamp = "|".join([_safe_mtime(train_csv), _safe_mtime(svm_pkl), _safe_mtime(tfidf_pkl)])
    digest = hashlib.md5(stamp.encode("utf-8")).hexdigest()[:10]
    return f"v{digest}"


CACHE_NAMESPACE = _compute_cache_namespace()

def get_cached_answer(query_text: str):
    try:
        namespaced = f"{CACHE_NAMESPACE}:{query_text}"
        entry = CachedAnswer.objects.get(query_text=namespaced)
        if entry.expires_at > timezone.now():
            return entry.answer
        entry.delete()
    except CachedAnswer.DoesNotExist:
        return None
    return None

def set_cached_answer(query_text: str, answer: str, ttl_days: int = DEFAULT_TTL_DAYS):
    expires_at = timezone.now() + timedelta(days=ttl_days)
    namespaced = f"{CACHE_NAMESPACE}:{query_text}"
    CachedAnswer.objects.update_or_create(
        query_text=namespaced,
        defaults={"answer": answer, "expires_at": expires_at}
    )

def clear_expired_cache():
    now = timezone.now()
    CachedAnswer.objects.filter(expires_at__lte=now).delete()


def clear_all_cache():
    """Dangerous: wipe all cached answers. Useful after large dataset updates."""
    CachedAnswer.objects.all().delete()
