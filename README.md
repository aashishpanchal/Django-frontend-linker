
# Django-frontend-linker

This django app adds a management command. you can easily to link react build bundle/dir

in django project.

Installation
------------

Add ``'frontlink'`` to the ``INSTALLED_APPS``

    INSTALLED_APPS = (
        ...
        'frontlink',
        ...
    )
Add ``'frontlink url'`` in project urls.py
```python
    from django.contrib import admin
    from django.urls import path, include
    
    urlpatterns = [
        path('admin/', admin.site.urls),
        ...
        path('', include('frontlink.urls')),
    ]
```
Usage
-----
    $ python manage.py frontlink --dir <path> --build-name <dir-name>

``'--dir'`` is required path of react/next build directory.

### Example:
    $ python manage.py frontlink --dir D:\react-project\hello-world

``'--build-name'`` is optional and but is required name of the react/next build folder name


### Example
    $ py manage.py frontlink --dir D:\react-project\hello-world --build-name hello

Clean previous build dir, so use:

    $ python manage.py frontlink --dir <path> --clear

Configuration
-------------
```python
    DEFAULTS = {
        'FRONTEND_ROOT': BASE_DIR / 'build_staticfiles',
        'FRONTEND_URL': '',
    }
```
