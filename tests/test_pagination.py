import flask
import pytest
import copy
from werkzeug.exceptions import NotFound

from flask_mongoengine import ListFieldPagination, Pagination, KeysetPagination


@pytest.fixture(autouse=True)
def setup_endpoints(app, todo):
    Todo = todo
    for i in range(42):
        Todo(title=f"post: {i}").save()

    @app.route("/")
    def index():
        page = int(flask.request.form.get("page"))
        per_page = int(flask.request.form.get("per_page"))
        query_set = Todo.objects().paginate(page=page, per_page=per_page)
        return {'data': [_ for _ in query_set.items],
                'total': query_set.total,
                'has_next': query_set.has_next,
                }


def test_queryset_paginator(app, todo):
    Todo = todo
    with pytest.raises(NotFound):
        Pagination(iterable=Todo.objects, page=0, per_page=10)

    with pytest.raises(NotFound):
        Pagination(iterable=Todo.objects, page=6, per_page=10)

    paginator = Pagination(Todo.objects, 1, 10)
    _test_paginator(paginator)

    for page in range(1, 10):
        for index, todo in enumerate(
            Todo.objects.paginate(page=page, per_page=5).items
        ):
            assert todo.title == f"post: {(page-1) * 5 + index}"


def test_keyset_queryset_paginator(app, todo):
    Todo = todo

    last_field_value = None
    for page in range(1, 10):
        p = Todo.objects.paginate_by_keyset(per_page=5, field_filter_by='id', last_field_value=last_field_value)
        for index, todo in enumerate(p.items):
            assert todo.title == f"post: {(page-1) * 5 + index}"
        last_field_value = list(p.items)[-1].pk

    # Pagination
    paginator = KeysetPagination(Todo.objects, per_page=5, field_filter_by='id')
    for page_index, page in enumerate(paginator):
        for index, todo in enumerate(page.items):
            assert todo.title == f"post: {(page_index) * 5 + index}"

    # Pagination with prev function
    paginator_2 = KeysetPagination(Todo.objects, per_page=5, field_filter_by='id')
    a = copy.deepcopy(paginator_2.next().items)
    paginator_2.next()
    a2 = paginator_2.prev().items
    for index, item in enumerate(a2):
        assert a[4-index].title == item.title


def test_paginate_plain_list():
    with pytest.raises(NotFound):
        Pagination(iterable=range(1, 42), page=0, per_page=10)

    with pytest.raises(NotFound):
        Pagination(iterable=range(1, 42), page=6, per_page=10)

    paginator = Pagination(range(1, 42), 1, 10)
    _test_paginator(paginator)


def test_list_field_pagination(app, todo):
    Todo = todo

    comments = [f"comment: {i}" for i in range(42)]
    todo = Todo(
        title="todo has comments",
        comments=comments,
        comment_count=len(comments),
    ).save()

    # Check without providing a total
    paginator = ListFieldPagination(Todo.objects, todo.id, "comments", 1, 10)
    _test_paginator(paginator)

    # Check with providing a total (saves a query)
    paginator = ListFieldPagination(
        Todo.objects, todo.id, "comments", 1, 10, todo.comment_count
    )
    _test_paginator(paginator)

    paginator = todo.paginate_field("comments", 1, 10)
    _test_paginator(paginator)


def _test_paginator(paginator):
    assert 5 == paginator.pages
    assert [1, 2, 3, 4, 5] == list(paginator.iter_pages())

    for i in [1, 2, 3, 4, 5]:

        if i == 1:
            assert not paginator.has_prev
            with pytest.raises(NotFound):
                paginator.prev()
        else:
            assert paginator.has_prev

        if i == 5:
            assert not paginator.has_next
            with pytest.raises(NotFound):
                paginator.next()
        else:
            assert paginator.has_next

        if i == 3:
            assert [None, 2, 3, 4, None] == list(paginator.iter_pages(0, 1, 1, 0))

        assert i == paginator.page
        assert i - 1 == paginator.prev_num
        assert i + 1 == paginator.next_num

        # Paginate to the next page
        if i < 5:
            paginator = paginator.next()



def test_flask_pagination(app, todo):
    client = app.test_client()
    response = client.get(f"/", data={"page": 0, "per_page": 10})
    print(response.status_code)
    assert response.status_code == 404

    response = client.get(f"/", data={"page": 6, "per_page": 10})
    print(response.status_code)
    assert response.status_code == 404


def test_flask_pagination_next(app, todo):
    client = app.test_client()
    has_next = True
    page = 1
    while has_next:
        response = client.get(f"/", data={"page": page, "per_page": 10})
        assert response.status_code == 200
        has_next = response.json['has_next']
        page += 1
