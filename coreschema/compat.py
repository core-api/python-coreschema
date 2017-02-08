import sys

if sys.version_info.major == 2:
    text_types = (str, unicode)
else:
    text_types = str
