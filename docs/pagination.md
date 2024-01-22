# Pagination

flask-mongoengine attaches the following methods to Mongoengine's default QuerySet:

* **paginate**: paginates the QuerySet. Takes two required arguments, *page* and *per_page*.
   And two optional arguments: *max_depth*, *first_page_index*.
* **paginate_by_keyset**: paginates the QuerySet. Takes two required arguments,
  *per_page* and *field_filter_by*.
  from the second page you need also the last id of the previous page.
  Arguments: *per_page*, *field_filter_by*, *last_field_value*.
* **paginate_field**: paginates a field from one document in the QuerySet.
  Arguments: *field_name*, *doc_id*, *page*, *per_page*.
  And two optional arguments: *total*, *first_page_index*

## Offset pagination

Offset API pagination is the most common form of API pagination.
It’s also sometimes called page-based pagination.
An API endpoint accepts a parameter for a page number and per page then
returns that page values.

### Example 1

```python
from flask import request

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)

paginated_todos = Todo.objects.paginate(page=page, per_page=per_page)

```

### Example 2

```python
from flask import request
from flask_mongoengine import Pagination

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)

Pagination(Todo.objects, page=page, per_page=10)
```

## Keyset pagination

Keyset-based API pagination is when an API provides a key parameter that
delineates the query results.
One example is if an API is sorted by ID, one key parameter could be since_id.

Keyset pagination is a great way to paginate through a large dataset
without having to worry about the page number.
It also allows for a more consistent user experience as the user can
always see the same results when they go to the next page.

### Example 1

```python
from flask import request

field_filter_by = '_id'
per_page = request.args.get('per_page', 10, type=int)

paginated_todos = Todo.objects.paginate_by_keyset(per_page=per_page, field_filter_by=field_filter_by)

# PAGE 2
paginated_todos_2 = Todo.objects.paginate_by_keyset(per_page=per_page, field_filter_by=field_filter_by,
                                                    last_field_value='value_of last page')
```

### Example 2

```python
from flask import request
from flask_mongoengine import KeysetPagination

field_filter_by = '_id'
per_page = request.args.get('per_page', 10, type=int)


KeysetPagination(Todo.objects, per_page=per_page, field_filter_by=field_filter_by)
```

## List field pagination

List field pagination is when an API provides a key parameter that is
the field name that is list of values and paginate on this list.

## Example 1

```python
from flask import request

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)
todo_id = request.args.get('todo_id', 10)

todo = Todo.objects.get_or_404(_id=todo_id)
paginated_tags = todo.paginate_field(field_name='tags', page=page, per_page=per_page)
```

## Example 2

```python
from flask import request

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)
todo_id = request.args.get('todo_id', 10)


paginated_tags = Todo.paginate_field(Todo.objects, doc_id=todo_id, field_name='tags',
                                     page=page, per_page=per_page)
```

## Example 3

```python
from flask import request
from flask_mongoengine import ListFieldPagination

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)
todo_id = request.args.get('todo_id', 10)


ListFieldPagination(Todo.objects, doc_id=todo_id, field_name='tags',
                    page=page, per_page=per_page)
```

## Render page with pagination

Properties of the pagination object include: iter_pages, next, prev, has_next,
has_prev, next_num, prev_num.

In the template:

```html
{# Display a page of todos #}
<ul>
    {% for todo in paginated_todos.items %}
        <li>{{ todo.title }}</li>
    {% endfor %}
</ul>

{# Macro for creating navigation links #}
{% macro render_navigation(pagination, endpoint) %}
  <div class=pagination>
  {% for page in pagination.iter_pages() %}
    {% if page %}
      {% if page != pagination.page %}
        <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
      {% else %}
        <strong>{{ page }}</strong>
      {% endif %}
    {% else %}
      <span class=ellipsis>…</span>
    {% endif %}
  {% endfor %}
  </div>
{% endmacro %}

{{ render_navigation(paginated_todos, 'view_todos') }}
```
