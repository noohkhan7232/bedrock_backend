from langchain_core.documents import Document


LANDING = (
'''
# Bedrock Homepage
TBD
'''
).strip()


LANDING_DOCUMENTS = [
  Document(
    page_content=LANDING,
    metadata={
      'source': 'landing-page',
      'url': '',
      'lang': 'en',
    },
  ),
]
