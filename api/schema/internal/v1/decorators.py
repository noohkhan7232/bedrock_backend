from api.schema.decorators import make_extend_class_schema
from api.schema.internal.v1.tags import API_TAGS


extend_class_schema = make_extend_class_schema(api_tags=API_TAGS)
