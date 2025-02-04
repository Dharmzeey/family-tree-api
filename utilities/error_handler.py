def render_errors(errors):
  """_summary_
    Renders the error messages from the serializer.errors dictionary.

  Args:
      errors (_type_): serializer.errors

  Returns:
      _type_: Dict[str, list]
  """
  custom_errors = {}
  for field, errors in errors.items():
    custom_errors[field] = ', '.join(errors)
  return custom_errors