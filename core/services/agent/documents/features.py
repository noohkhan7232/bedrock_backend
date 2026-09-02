from langchain_core.documents import Document


WORKFLOWS = (
'''
# Workflows & Architecture
TBD
'''
)


ESSENTIAL_FUNCTIONS = (
'''
# Essential Functions
TBD
'''
)


ANTI_PATTERNS = (
'''
# Anti-Patterns
TBD
'''
)


FEATURE_DOCUMENTS = [
  Document(
    page_content=WORKFLOWS,
    metadata={
      'source': 'official-doc',
      'url': '',
      'lang': 'en',
    },
  ),
  Document(
    page_content=ESSENTIAL_FUNCTIONS,
    metadata={
      'source': 'official-doc',
      'url': '',
      'lang': 'en',
    },
  ),
  Document(
    page_content=ANTI_PATTERNS,
    metadata={
      'source': 'official-doc',
      'url': '',
      'lang': 'en',
    },
  ),
]
