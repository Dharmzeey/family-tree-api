# def render_errors(errors):
#   """_summary_
#     Renders the error messages from the serializer.errors dictionary.

#   Args:
#       errors (_type_): serializer.errors

#   Returns:
#       _type_: Dict[str, list]
#   """
#   custom_errors = {}
#   for field, errors in errors.items():
#     custom_errors[field] = ', '.join(errors)
#   return custom_errors


def render_errors(errors):
    """
    Renders the error messages from the serializer.errors dictionary into a single string.

    Args:
        errors (dict): The serializer.errors dictionary.

    Returns:
        str: A single concatenated string of all error messages.
    """
    error_messages = []

    # Recursively flatten the errors
    def flatten_errors(error_dict):
        for field, error_list in error_dict.items():
            if isinstance(error_list, dict):
                # If the error is nested, recursively process it
                flatten_errors(error_list)
            elif isinstance(error_list, list):
                # If it's a list of errors, join them into a single string
                error_messages.append(f"{field}: {', '.join(error_list)}")
            else:
                # If it's a single error, add it directly
                error_messages.append(f"{field}: {error_list}")

    flatten_errors(errors)
    return ' '.join(error_messages)  # Join all errors into a single string