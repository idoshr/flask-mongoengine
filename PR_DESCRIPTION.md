# Pull Request: Fix critical pagination bugs

## PR Title
Fix critical pagination bugs: prevent crashes from invalid per_page values

## Summary
This PR fixes critical pagination bugs that can cause application crashes. It includes a comprehensive bug report and fixes for the two highest-priority issues.

## Changes

### 1. Bug Report (BUG_REPORT.md)
Added comprehensive documentation of 6 pagination bugs found during code review:
- **Critical**: Division by zero with `per_page=0` (Bug #4)
- **Critical**: Negative `per_page` values cause undefined behavior (Bug #5)
- **Medium**: `iter_pages()` left edge calculation incorrect (Bug #1)
- **Medium**: `iter_pages()` right edge calculation incorrect (Bug #2)
- **Low**: Useless `assert NotImplementedError` statement (Bug #3)
- **Low**: `prev_num`/`next_num` don't check boundaries (Bug #6)

### 2. Critical Bug Fixes
Fixed Bugs #4 and #5 by adding validation to prevent invalid `per_page` values:

**Modified Files:**
- `flask_mongoengine/pagination/basic_pagination.py`
- `flask_mongoengine/pagination/keyset_pagination.py`
- `flask_mongoengine/pagination/list_field_pagination.py`

**Changes:**
- Added validation: `if per_page <= 0: raise ValueError("per_page must be a positive integer")`
- Prevents `ZeroDivisionError` crashes when `per_page=0`
- Prevents undefined behavior with negative `per_page` values
- Raises clear, actionable error messages

**Test Coverage:**
- Added `test_per_page_validation()` in `tests/test_pagination.py`
- Tests all three pagination classes (Pagination, KeysetPagination, ListFieldPagination)
- Verifies correct `ValueError` is raised for both `per_page=0` and negative values
- Includes proper error message matching

## Impact

### Before
```python
# Division by zero - CRASH!
paginator = Pagination(data, 1, 0)
pages = paginator.pages  # ZeroDivisionError

# Negative per_page - nonsensical results
paginator = Pagination(data, 1, -5)
print(paginator.pages)  # -2 (what does this even mean?)
```

### After
```python
# Clear error message
paginator = Pagination(data, 1, 0)
# ValueError: per_page must be a positive integer

# Prevents undefined behavior
paginator = Pagination(data, 1, -5)
# ValueError: per_page must be a positive integer
```

## Testing
- Added comprehensive test coverage for all pagination classes
- Tests verify both zero and negative `per_page` values are rejected
- Tests confirm proper error messages are raised

## Future Work
The BUG_REPORT.md documents additional bugs that should be addressed in future PRs:
- Medium priority: `iter_pages()` edge calculation bugs (Bugs #1, #2)
- Low priority: Code quality improvements (Bugs #3, #6)

## Related Issues
Fixes critical stability issues that could cause production crashes.

---

## How to Create the PR

Since GitHub CLI is not available, create the PR manually:

1. Go to: https://github.com/idoshr/flask-mongoengine/pull/new/claude/review-pagination-bugs-011CUfCDfh8bqjSDYMjCyeov
2. Use the title and description above
3. Submit the PR

Branch: `claude/review-pagination-bugs-011CUfCDfh8bqjSDYMjCyeov`
