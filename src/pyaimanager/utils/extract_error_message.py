def extract_error_message(e):
    """
    Extracts the error message from an exception.

    If the exception is an instance of requests.exceptions.HTTPError, this function
    will try to extract the error message from the JSON response.

    If the exception is not an instance of requests.exceptions.HTTPError, this function
    will try to extract the error message using a regular expression that matches the
    content inside the first pair of curly braces {}. If the regular expression doesn't
    find a match, it will use the entire exception message as the error message.

    Args:
        e (Exception): The exception to extract the error message from.

    Returns:
        str: The extracted error message.
    """

    if isinstance(e, requests.exceptions.HTTPError):
        error_json = e.response.json()
        return error_json.get('error', {}).get('message', str(e))
    else:
        error_message = re.search(r'(\{.*\})', str(e), re.DOTALL)
        if error_message:
            return error_message.group(1)  # Get the matched string
        else:
            return str(e)