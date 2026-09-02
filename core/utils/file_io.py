import uuid
import warnings
from pathlib import Path

from django.core.files import File
from PIL import Image, UnidentifiedImageError

from core.constants.file_io import (
  DEFAULT_IMAGE_UPLOAD_RULES,
  ImageUploadRule,
)
from core.exceptions import DomainValidationError


def get_file_extension(file: File) -> str:
  return Path(file.name).suffix.lower()


def rename_file(file: File, prefix='') -> None:
  ext = get_file_extension(file=file)
  file.name = f'{prefix}{uuid.uuid4().hex}{ext}'


def _ensure_filename(file: File) -> None:
  original_name = file.name
  if not original_name:
    raise DomainValidationError('Missing file name.')

  if Path(original_name).name != original_name:
    raise DomainValidationError('Invalid file name.')


def _ensure_image_file(file: File) -> None:
  file.seek(0)

  with warnings.catch_warnings():
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    with Image.open(file) as image:
      image.verify()


def _read_image_metadata(file: File) -> tuple[str | None, int, int]:
  file.seek(0)

  with warnings.catch_warnings():
    warnings.simplefilter('error', Image.DecompressionBombWarning)
    with Image.open(file) as image:
      return image.format, image.width, image.height


def ensure_image_file(
  file: File,
  rule: ImageUploadRule = DEFAULT_IMAGE_UPLOAD_RULES.MEDIUM,
) -> File:
  ext = get_file_extension(file=file)
  if ext not in rule.allowed_extensions:
    raise DomainValidationError('Unsupported image file extension.')

  if file.size > rule.max_bytes:
    raise DomainValidationError('Image file is too large.')

  content_type = getattr(file, 'content_type', None)
  if content_type and content_type not in rule.allowed_content_types:
    raise DomainValidationError('Unsupported image content type.')

  original_pos: int | None
  try:
    original_pos = file.tell()
  except (AttributeError, OSError):
    original_pos = None

  try:
    _ensure_filename(file=file)
    _ensure_image_file(file=file)
    image_format, width, height = _read_image_metadata(file=file)

    if image_format not in rule.allowed_formats:
      raise DomainValidationError('Unsupported image format.')

    if width > rule.max_width:
      raise DomainValidationError('Image width is too large.')

    if height > rule.max_height:
      raise DomainValidationError('Image height is too large.')

    if width * height > rule.max_pixels:
      raise DomainValidationError('Image has too many pixels.')
  except (
      UnidentifiedImageError,
      Image.DecompressionBombWarning,
      Image.DecompressionBombError,
      OSError,
  ) as e:
    raise DomainValidationError('Invalid image file.') from e
  finally:
    try:
      file.seek(original_pos if original_pos is not None else 0)
    except (AttributeError, OSError):
      pass

  return file
