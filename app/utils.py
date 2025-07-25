import random
import string
from urllib.parse import urlparse

# Constants for code length(set to 6) and alphanumeric characters
CODE_LENGTH = 6
ALPHANUM = string.ascii_letters + string.digits

def generate_short_code():
    """
    @Description:
        Generate a random alphanumeric short code of fixed length for URL shortening.
    @Returns:
        str: A randomly generated alphanumeric string of length CODE_LENGTH.
    """

    return ''.join(random.choices(ALPHANUM, k=CODE_LENGTH))

def is_valid_url(url):
    """
    @Description:
        Validate whether a string is a well-formed HTTP or HTTPS URL.
        Checks that the URL has a valid scheme (http or https) and a network location (netloc).
    @Args:
        url (str): The URL string to validate.
    @Returns:
        bool: True if the URL is valid (http/https and has netloc), False otherwise.
    """
    
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False