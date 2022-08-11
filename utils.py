import validators


def validate_url(url: str) -> bool:
    try:
        return validators.url(url)
    except validators.ValidationFailure as err:
        print(
            f'URL validation failed, please check your URL again.\nHere are error details: {err}')
        return False
