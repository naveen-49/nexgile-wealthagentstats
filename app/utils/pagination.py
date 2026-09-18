def paginate_query(query, serializer, page=1, per_page=10):
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        "data": [
            serializer(item)
            for item in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }