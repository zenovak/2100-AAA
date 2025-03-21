def parser(template_string: str, context: dict):
    """

    :param template_string: the raw string to template
    :param context: context object, which is a collection of key-value.
    :return:
    """

    return template_string.format(**context)