def format_response(message: str, data=None, status_text: str = "success"):
    return {
        "message": message,
        "status": status_text,
        "data": data,
    }