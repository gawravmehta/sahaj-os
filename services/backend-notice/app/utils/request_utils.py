from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Gets the client's real IP address from the request."""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0]
    return request.client.host
