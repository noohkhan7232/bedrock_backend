from langchain_core.documents import Document

from core.constants.base import CONSTANTS


ABOUT_US = (
'''
# About Bedrock
'''
)


RESOURCES = (
f'''
# Bedrock Resources
- Support: {CONSTANTS.CONTACTS.API_SUPPORT_CONTACT},
- Help Center/Document: {CONSTANTS.CONTACTS.HELP_CENTER_URL},
- Official website/Landing page: {CONSTANTS.CONTACTS.LANDING_PAGE_URL},
- Terms of Service: {CONSTANTS.CONTACTS.TERMS_OF_SERVICE_URL},
- Privacy Policy: {CONSTANTS.CONTACTS.PRIVACY_POLICY_URL},
- California Notice URL: {CONSTANTS.CONTACTS.CALIFORNIA_NOTICE_URL},
- Service Owner Address: {CONSTANTS.CONTACTS.SERVICE_OWNER_ADDRESS},
'''
)


ABOUT_DOCUMENTS = [
  Document(
    page_content=ABOUT_US,
    metadata={
      'source': 'official-website',
      'url': '',
      'lang': 'en',
    },
  ),
  Document(
    page_content=RESOURCES,
    metadata={
      'source': 'official-website',
      'url': '',
      'lang': 'en',
    },
  ),
]
