from typing import Callable, TypeVar

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q, Value
from django.db.models.functions import Concat, Greatest
from rest_framework.request import Request

T = TypeVar('T')


def get_query_param(
  request: Request,
  key: str,
  fallback: T | None =None,
  cast: Callable[[str], T] = str,
  strip: bool = True,
  empty_as_none: bool = True,
) -> T | None:
  value = request.query_params.get(key, None)

  if value is None:
    return fallback

  if isinstance(value, str) and strip:
    value = value.strip()

  if empty_as_none and value == '':
    return fallback

  try:
    return cast(value)
  except (TypeError, ValueError,):
    return fallback


def filter_user_by_text(
  query,
  text,
  fuzzy_match_email=False,
  match_email=False,
  prefix='',
  similarity_thresh=0.5,
):
  first_name = f'{prefix}first_name'
  last_name = f'{prefix}last_name'
  email = f'{prefix}email'

  similarities = ['__name_similarity', '__fn_similarity', '__ln_similarity']

  query = query\
    .annotate(__name=Concat(first_name, Value(' '), last_name))\
    .annotate(__name_similarity=TrigramSimilarity('__name', text))\
    .annotate(__fn_similarity=TrigramSimilarity(first_name, text))\
    .annotate(__ln_similarity=TrigramSimilarity(last_name, text))\

  if fuzzy_match_email:
    query = query\
      .annotate(__email_similarity=TrigramSimilarity(email, text))
    similarities.append('__email_similarity')

  query = query.annotate(__similarity=Greatest(*[F(f) for f in similarities]))
  cond = Q(__similarity__gt=similarity_thresh)

  if match_email:
    cond |= Q(**{f'{email}__icontains': text})

  return query.filter(cond).order_by('__similarity')
