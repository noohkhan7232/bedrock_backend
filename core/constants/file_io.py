from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class ImageUploadRule:
  max_bytes: int
  allowed_extensions: tuple[str, ...]
  allowed_formats: tuple[str, ...]
  allowed_content_types: tuple[str, ...]
  max_width: int
  max_height: int
  max_pixels: int


@dataclass(frozen=True, slots=True)
class ImageUploadRules:
  SMALL: ImageUploadRule = ImageUploadRule(
    max_bytes=1 * 1024 * 1024,
    allowed_extensions=('.jpg', '.jpeg', '.png',),
    allowed_formats=('JPEG', 'PNG',),
    allowed_content_types=('image/jpeg', 'image/png',),
    max_width=1024,
    max_height=1024,
    max_pixels=1_048_576,
  )
  MEDIUM: ImageUploadRule = ImageUploadRule(
    max_bytes=3 * 1024 * 1024,
    allowed_extensions=('.jpg', '.jpeg', '.png',),
    allowed_formats=('JPEG', 'PNG',),
    allowed_content_types=('image/jpeg', 'image/png',),
    max_width=2048,
    max_height=2048,
    max_pixels=4_194_304,
  )
  LARGE: ImageUploadRule = ImageUploadRule(
    max_bytes=5 * 1024 * 1024,
    allowed_extensions=('.jpg', '.jpeg', '.png',),
    allowed_formats=('JPEG', 'PNG',),
    allowed_content_types=('image/jpeg', 'image/png',),
    max_width=4096,
    max_height=4096,
    max_pixels=16_777_216,
  )


DEFAULT_IMAGE_UPLOAD_RULES: Final[ImageUploadRules] = ImageUploadRules()
