import sys


# syntax
HAS_WALRUS_OP = sys.version_info >= (3, 8)
HAS_MATCH_CASE = sys.version_info >= (3, 10)
HAS_EXCEPTION_GROUP = sys.version_info >= (3, 11)

# operator
HAS_TYPE_UNION = sys.version_info >= (3, 10)
