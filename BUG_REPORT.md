# Pagination Bugs Report

## Summary
This report documents several bugs found in the flask-mongoengine pagination implementation. The bugs range from incorrect edge case handling in `iter_pages()` to potential crashes and useless code.

---

## Bug #1: `iter_pages()` left_edge calculation is incorrect when `first_page_index != 1`

**File**: `flask_mongoengine/pagination/basic_pagination.py:142`
**Severity**: Medium
**Status**: Confirmed

### Description
The condition `num <= left_edge` doesn't account for the `first_page_index` offset. This causes the wrong number of pages to be shown on the left edge when using a custom `first_page_index`.

### Current Code
```python
if (
    num <= left_edge  # BUG: Doesn't account for first_page_index
    or num > self.pages - right_edge
    or (num >= self.page - left_current and num <= self.page + right_current)
):
```

### Problem
- When `first_page_index=1` and `left_edge=2`: `num <= 2` matches pages 1, 2 ✓ (works by accident)
- When `first_page_index=0` and `left_edge=2`: `num <= 2` matches pages 0, 1, 2 ✗ (should only match 0, 1)
- When `first_page_index=5` and `left_edge=2`: `num <= 2` matches nothing ✗ (should match pages 5, 6)

### Fix
```python
num < left_edge + self.first_page_index
```

### Test Case
```python
# With 10 pages, first_page_index=0, left_edge=2
paginator = Pagination(data, 4, 10, first_page_index=0)
pages = list(paginator.iter_pages(left_edge=2, right_edge=2))
# Current result: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] (shows 3 left edge pages)
# Expected result: [0, 1, None, 2, 3, 4, 5, 6, 7, 8, 9] (shows 2 left edge pages)
```

---

## Bug #2: `iter_pages()` right_edge calculation is incorrect when `first_page_index != 1`

**File**: `flask_mongoengine/pagination/basic_pagination.py:143`
**Severity**: Medium
**Status**: Confirmed

### Description
The condition `num > self.pages - right_edge` doesn't properly account for `first_page_index`. It compares an absolute page number (`num`) with a count-based calculation (`self.pages - right_edge`).

### Current Code
```python
if (
    num <= left_edge
    or num > self.pages - right_edge  # BUG: Incorrect calculation
    or (num >= self.page - left_current and num <= self.page + right_current)
):
```

### Problem
- When `first_page_index=1`, `pages=10`, `right_edge=2`:
  - `num > 10 - 2 = 8` matches pages 9, 10 ✓ (works by accident)
- When `first_page_index=0`, `pages=10`, `right_edge=2`:
  - `num > 10 - 2 = 8` matches page 9 only ✗ (should match pages 8, 9)
  - `last_page_index = 9` (0-indexed), so should show pages 8, 9

### Fix
```python
num > self.last_page_index - right_edge
```
or equivalently:
```python
num > self.pages + self.first_page_index - 1 - right_edge
```

### Test Case
```python
# With 10 pages, first_page_index=0, right_edge=2
paginator = Pagination(data, 4, 10, first_page_index=0)
pages = list(paginator.iter_pages(left_edge=2, right_edge=2))
# Current result: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] (shows 1 right edge page)
# Expected result: [0, 1, None, 2, 3, 4, 5, 6, 7, 8, 9] (shows 2 right edge pages)
```

---

## Bug #3: Useless `assert NotImplementedError` in `prev()` method

**File**: `flask_mongoengine/pagination/keyset_pagination.py:69`
**Severity**: Low
**Status**: Confirmed

### Description
The line `assert NotImplementedError` does nothing because `NotImplementedError` (the class) is always truthy. This appears to be leftover code from when the method was abstract.

### Current Code
```python
def prev(self, error_out=False):
    assert NotImplementedError  # BUG: This does nothing
    """Returns a :class:`Pagination` object for the previous page."""
    assert (
        self.iterable is not None
    ), "an object is required for this method to work"
    # ... rest of implementation
```

### Problem
- `assert NotImplementedError` evaluates `assert True`, which passes and does nothing
- The docstring is incorrectly placed after code (not a bug, but poor style)
- If the intent was to raise an exception, it should be `raise NotImplementedError`
- If the intent was to check something, the assert is meaningless

### Fix
Simply remove the line:
```python
def prev(self, error_out=False):
    """Returns a :class:`Pagination` object for the previous page."""
    assert (
        self.iterable is not None
    ), "an object is required for this method to work"
    # ... rest of implementation
```

---

## Bug #4: Division by zero when `per_page=0`

**File**: `flask_mongoengine/pagination/abc_pagination.py:9` and `basic_pagination.py:53`
**Severity**: High
**Status**: Confirmed

### Description
No validation exists to prevent `per_page=0`, which causes a `ZeroDivisionError` when accessing the `pages` property.

### Current Code
```python
@property
def pages(self) -> int:
    """The total number of pages"""
    return int(math.ceil(self.total / float(self.per_page)))  # ZeroDivisionError if per_page=0
```

### Problem
```python
paginator = Pagination(data, 1, 0)  # per_page=0
pages = paginator.pages  # Crashes with ZeroDivisionError
```

### Fix
Add validation in `__init__` methods:
```python
def __init__(self, iterable, page: int, per_page: int, ...):
    if per_page <= 0:
        raise ValueError("per_page must be a positive integer")
    # ... rest of init
```

---

## Bug #5: Negative `per_page` creates nonsensical results

**File**: All pagination classes
**Severity**: Medium
**Status**: Confirmed

### Description
No validation prevents negative `per_page` values, which creates negative page counts and nonsensical behavior.

### Problem
```python
paginator = Pagination(data, 1, -5)  # per_page=-5
print(paginator.pages)  # -2 (nonsensical)
```

### Fix
Same as Bug #4 - validate in `__init__`:
```python
if per_page <= 0:
    raise ValueError("per_page must be a positive integer")
```

---

## Bug #6: `prev_num` and `next_num` don't check boundaries

**File**: `flask_mongoengine/pagination/abc_pagination.py:17-19` and `basic_pagination.py:72-74, 108-110`
**Severity**: Low
**Status**: Confirmed

### Description
The `prev_num` and `next_num` properties return page numbers without checking if those pages exist. While `has_prev` and `has_next` exist for checking, the `*_num` properties can return invalid page numbers.

### Current Code
```python
@property
def prev_num(self) -> int:
    """Number of the previous page."""
    return self.page - 1  # Can return invalid page number

@property
def next_num(self) -> int:
    """Number of the next page"""
    return self.page + 1  # Can return invalid page number
```

### Problem
```python
paginator = Pagination(data, 1, 10)  # First page
print(paginator.prev_num)  # Returns 0, which is invalid when first_page_index=1
```

### Note
This may be intentional design (caller should check `has_prev`/`has_next`), but it could lead to bugs if users don't check. Consider documenting this behavior clearly or returning `None` for invalid pages.

---

## Impact Assessment

### High Priority (Should fix immediately)
- Bug #4: Division by zero (causes crashes)
- Bug #5: Negative per_page (undefined behavior)

### Medium Priority (Should fix in next release)
- Bug #1: Left edge calculation (incorrect behavior with custom first_page_index)
- Bug #2: Right edge calculation (incorrect behavior with custom first_page_index)

### Low Priority (Code quality)
- Bug #3: Useless assert statement (no functional impact)
- Bug #6: Unchecked prev_num/next_num (may be by design)

---

## Testing Recommendations

1. Add test cases for `iter_pages()` with various `first_page_index` values
2. Add validation tests for `per_page <= 0`
3. Add edge case tests for empty result sets
4. Add tests for large pagination (100+ pages) with custom first_page_index

---

## Additional Notes

The existing test suite doesn't catch these bugs because:
- `test_queryset_paginator_first_page_index()` uses default `iter_pages()` parameters which happen to work
- No tests exist for `per_page <= 0`
- No tests exist for large pagination with ellipsis (None values in iter_pages)

The test at line 157-158 is commented out but would have caught bugs #1 and #2:
```python
# if i == 3:
#     assert [None, 2, 3, 4, None] == list(paginator.iter_pages(0, 1, 1, 0))
```
