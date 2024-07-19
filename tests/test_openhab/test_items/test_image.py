from HABApp.openhab.items import ImageItem
from HABApp.openhab.map_items import map_item


def test_image_load():

    i = map_item(
        'localCurrentConditionIcon',
        'Image',
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPwAAAD8CAYAAABTq8lnAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFIGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDAgNzkuMTYwNDUxLCAyMDE3LzA1LzA2LTAxOjA4OjIxICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoTWFjaW50b3NoKSIgeG1wOkNyZWF0ZURhdGU9IjIwMTgtMDgtMTdUMTQ6MTc6NTAtMDQ6MDAiIHhtcDpNb2RpZnlEYXRlPSIyMDE4LTA4LTIwVDA3OjM4OjE2LTA0OjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE4LTA4LTIwVDA3OjM4OjE2LTA0OjAwIiBkYzpmb3JtYXQ9ImltYWdlL3BuZyIgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIgcGhvdG9zaG9wOklDQ1Byb2ZpbGU9InNSR0IgSUVDNjE5NjYtMi4xIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjJiNzE4NDBmLTE2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",
        label='',
        tags=frozenset(),
        groups=frozenset(),
        metadata=None,
    )

    assert isinstance(i, ImageItem)
    assert i.image_type == 'png'
    assert isinstance(i.value, bytes)
