from django.conf import settings

from core.constants import CONSTANTS


GENERAL_API_USAGE_NOTE = (
"""
**General API Usage Note:**
* **Resource Ownership:** Most of our APIs, particularly actions like POST, PUT, and DELETE, are typically reserved for the rightful owner of the relevant resource.
* **Access Restrictions:** Unauthorized attempts by non-owners will be blocked.
* **Tenant Admin Privileges:** In cases where resources are linked to a `tenant_user` rather than a `user`, tenant admins may often have the authority to access the API.
"""
)

EXTERNAL_API_DOC_TITLE = f'{settings.APP_NAME} API Documentation'
EXTERNAL_API_DOC_TOS = CONSTANTS.CONTACTS.TERMS_OF_SERVICE_URL
EXTERNAL_API_DOC_CONTACT = {
  'email': CONSTANTS.CONTACTS.API_SUPPORT_CONTACT,
}
EXTERNAL_API_DOC_DESCRIPTION = (
f"""
### **Overview**

Welcome to the {settings.APP_NAME} API Documentation. Here, you'll find information regarding the endpoints, data formats, and operations available for integration with our platform.

This documentation provides you with end-to-end details for each API endpoint, from request headers to response format.

**Licensing and Use:**
* **Non-Commercial Use:** Users are welcome to integrate with our platform for personal, non-commercial purposes. If you with to use our API for commercial intent or gain, explicit permission from our team is mandatory.
* **Commercial Integration**: Before integrating our platform for commercial use, users must contact us for proper licensing and agreement. Unauthorized commercial integrations are strictly prohibited and may result in legal actions.

**Important Notes:**
* **Dynamic Specification:** Our API specification may be added, deleted, or updated without any prior notifications. Stay updated by regularly checking the documentation.
* **Limited Public Availability:** Not all of our APIs are public and/or documented. Some endpoints may be restricted for internal use or specific partners.

{GENERAL_API_USAGE_NOTE}

As you explore, remember that our API is designed to be RESTful. For queries, please reach out to our developer support team at {CONSTANTS.CONTACTS.API_SUPPORT_CONTACT}.

Happy coding!
"""
)

INTERNAL_API_DOC_TITLE = f'{settings.APP_NAME} Internal API Documentation'
INTERNAL_API_DOC_TOS = CONSTANTS.CONTACTS.TERMS_OF_SERVICE_URL
INTERNAL_API_DOC_CONTACT = {
  'email': CONSTANTS.CONTACTS.API_SUPPORT_CONTACT,
}
INTERNAL_API_DOC_DESCRIPTION = (
f"""
### **Overview**

Hello Team,

Welcome to the internal API documentation for {settings.APP_NAME}. This guide is tailored for our development teams, ensuring seamless integration and understanding of our backend services.

This documentation provides you with end-to-end details for each API endpoint, from request headers to response format.

**Key Reminders:**
* **Dynamic Nature:** Our API evolves as our product does. Endpoints may be added, deprecated, or modified based on product needs. Stay updated.
* **Restricted Use:** This documentation covers internal endpoints that are not exposed to external partners or users. Treat this information confidently.
* **Development Environment:** For testing, always use the development environment to avoid disruptions to our live users.

{GENERAL_API_USAGE_NOTE}

**Contributing:**
We believe in the power of collective knowledge. If you find areas in the documentation that need clarity or if you've figured out some best practices, contribute! This document is a living entity, growing with our collective insights.

Forge ahead and code on!
"""
)

