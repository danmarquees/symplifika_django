import hashlib
from django import template

register = template.Library()


@register.filter
def md5(value):
    """
    Returns the MD5 hash of the given string.
    Used primarily for generating Gravatar URLs.
    """
    if value is None:
        return ''
    return hashlib.md5(value.encode('utf-8')).hexdigest()


@register.filter
def gravatar_url(email, size=80):
    """
    Returns a Gravatar URL for the given email address.
    Usage: {{ user.email|gravatar_url:150 }}
    """
    if not email:
        return ''

    email_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"


@register.filter
def initials(name):
    """
    Returns the initials of a name.
    Usage: {{ user.get_full_name|initials }}
    """
    if not name:
        return ''

    words = name.split()
    if len(words) == 1:
        return words[0][:1].upper()
    else:
        return ''.join([word[:1].upper() for word in words[:2]])


@register.filter
def file_size(bytes_value):
    """
    Returns a human-readable file size.
    Usage: {{ file.size|file_size }}
    """
    if not bytes_value:
        return '0 B'

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


@register.filter
def truncate_chars(value, length):
    """
    Truncates a string after a certain number of characters.
    Usage: {{ text|truncate_chars:50 }}
    """
    if not value:
        return ''

    if len(value) <= length:
        return value

    return value[:length] + '...'


@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ value|mul:10 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """
    Divides the value by the argument.
    Usage: {{ value|div:10 }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def sub(value, arg):
    """
    Subtracts the argument from the value.
    Usage: {{ value|sub:10 }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
