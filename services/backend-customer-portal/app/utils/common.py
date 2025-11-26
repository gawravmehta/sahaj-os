from datetime import datetime
import re

from bson import ObjectId


name_pattern = re.compile(r"^[A-Za-z]+$")


def clean_mongo_doc(doc):
    """Recursively convert MongoDB documents to JSON serializable format."""
    if isinstance(doc, list):
        return [clean_mongo_doc(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: clean_mongo_doc(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc
