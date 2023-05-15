# Let all or most files start with _ to designate them as internal, and only import here the things which are
#   used by other packages. This helps us to easily know what constitutes a breaking change, and what does not.

from excel_text._factory import get_text_function

text = get_text_function({"decimal": ".", "thousands": ",", "raise": True})
