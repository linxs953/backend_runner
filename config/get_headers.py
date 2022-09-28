DEFAULT_HEADERS = [
    {
        "key": "Content-Type",
        "value": "application/json"
    }
]


AUTH_VALUE = "{{$step_name.token_type}} {{$step_name.access_token}}"

def get_default_headers():
    return DEFAULT_HEADERS
