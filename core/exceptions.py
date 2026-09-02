class CoreError(Exception):
  """Base exception class for all custom exceptions in the core app."""
  pass


# --- Validation & Business Rule Errors ---

class AuthenticationFailedError(CoreError):
  """Raised when authentication failed."""
  pass


class ConflictError(CoreError):
  """Raised when data/logic conflicts."""
  pass


class DomainValidationError(CoreError):
  """Raised when a business rule or domain invariant is violated."""
  pass


class PermissionDeniedError(CoreError):
  """
  Raised when a user is not authorized to perform a specific business action.
  - Note: This is for BUSINESS-LEVEL permissions, not API-level authentication.
  - Maps to: 403 Forbidden
  """
  pass


class DuplicateRecordError(DomainValidationError):
  """
  Raised when a record creation fails due to a uniqueness constraint
  - Maps to: 409 Conflict
  """
  pass


class ResourceExpiredError(DomainValidationError):
  """
  Raised when a resource (e.g., tenant invitation code) is expired.
  - Maps to: 410 Gone
  """
  pass


class UsageLimitExceededError(DomainValidationError):
  """
  Raised when an action cannot be completed due to a usage limit.
  - Maps to: 403 Forbidden or 422 Unprocessable Entity
  """
  pass


class PayloadTooLargeError(DomainValidationError):
  """
  Raised when the request payload exceeds a size limit.
  - Note: This might also be handled by the web server (e.g., Nginx).
  - Maps to: 413 Payload Too Large
  """
  pass


# --- Data Access Errors ---

class ObjectNotFoundError(CoreError):
  """Raised when an expected object is not found in the database."""
  pass


class CodeNotFoundError(ObjectNotFoundError):
  """
  A specific 'not found' error for invitation/reset codes, etc.
  - Maps to: 404 Not Found
  """
  pass


class TooManyRequestsError(CoreError):
  """Raised when too many requests are done."""
  pass


# --- Infrastructure & External Service Errors ---

class ServiceError(CoreError):
  """Base class for external service failures."""
  pass


class EmailServiceError(ServiceError):
  """
  Raised when the email sending module fails.
  - Maps to: 503 Service Unavailable
  """
  pass


class SSOAuthenticationError(ServiceError):
  """
  Raised for errors related to Single Sign-On.
  - Maps to: 400 Bad Request
  """
  pass


# --- Special Control-Flow Exceptions ---

class NoActionTaken(Exception):
  """
  Raised when an operation is valid but results in no change,
  and this is an acceptable, successful outcome.
  - Note: This should NOT inherit from CoreError.
  - Maps to: 200 OK
  """
  pass


# --- AI Agent Exceptions ---

class ContentPolicyViolationError(Exception):
  """
  Raised when text content violates safety guidelines or content
  moderation policies.

  This exception is intended to be raised by guardrail mechanisms
  as unsafe, allowing the application to handle policy violations
  (e.g., OpenAI Moderation API) when the input text is flagged
  distinctly from generic validation errors.
  """
  pass


class JobCancelledError(BaseException):
  """
  Raised when an agent job is cancelled by the user.

  IMPORTANT:
  This exception inherits from `BaseException` instead of the standard
  `Exception`. This is a deliaberate design choice to ensure the cancellation
  signal propagates through any broad `try...except Exception` blocks that
  may exist within LangChain's internals or other third-party libraries.

  Treat this exception like a system-level interrupt (similar to
  KeyboardInterrupt).

  - Maps to: 200 OK
  """
  pass
