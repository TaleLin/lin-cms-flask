from flask import current_app, request


def get_count_from_query():
    count_default = current_app.config.get("COUNT_DEFAULT")
    count = int(request.args.get("count", count_default if count_default else 1))
    return count


def get_page_from_query():
    page_default = current_app.config.get("PAGE_DEFAULT")
    page = int(request.args.get("page", page_default if page_default else 0))
    return page


def paginate():
    from lin import ParameterError

    count = int(
        request.args.get(
            "count",
            current_app.config.get("COUNT_DEFAULT") if current_app.config.get("COUNT_DEFAULT") else 5,
        )
    )
    start = int(
        request.args.get(
            "page",
            current_app.config.get("PAGE_DEFAULT") if current_app.config.get("PAGE_DEFAULT") else 0,
        )
    )
    count = 15 if count >= 15 else count
    start = start * count
    if start < 0 or count < 0:
        raise ParameterError()
    return start, count
