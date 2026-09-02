from langchain_core.documents import Document


OVERVIEW_PAGE_CONTENT = (
'''
# Bedrock Overview
TBD
'''
)


PRICING = (
'''
## Bedrock Pricing
TBD
'''
)


PRODUCT_OVERVIEW = (
'''
# Bedrock Product Overviews
TBD
'''
)


OVERVIEW_DOCUMENTS = [
  Document(
    page_content=OVERVIEW_PAGE_CONTENT,
    metadata={
      'source': 'official-website',
      'url': '',
      'lang': 'en',
    },
  ),
  Document(
    page_content=PRICING,
    metadata={
      'source': 'official-website',
      'url': '',
      'lang': 'en',
    },
  ),
  Document(
    page_content=PRODUCT_OVERVIEW,
    metadata={
      'source': 'official-website',
      'url': '',
      'lang': 'en',
    },
  ),
]
