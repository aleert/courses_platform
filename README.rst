This is a small drf backend for e-learning platform.

WARNING
All api versions before v1 are not stable and subject to change at any moment.

Current api version: 0.1

Data model
==========
Here's high level overview of objects used in this project:

* Course - main object that holds information about students, teachers and other related info. Course consists of modules.

* Module - module within course, that maintain order via special OrderedField.

* Item - each module consists of one or more Item's that are used to store Content.
  Think of Item as of pages within module, where each page might hold multiple Content data.
  Items are ordered within module.

* Content - texts, video, files, assignments and any other stuff.
  Contents are ordered within Item. Note that you cannot create Content without Item by normal means.

Setup
=====
Run `pip install -r requirements.txt`, then navigate to `courses_platform` folder
and run `python manage.py runserver`, that's it.

Credentials
===========
There is a test database with superuser named 'alex' with a password 'test_password'.
Other users in test db should also have password 'test_password' but may vary.

Urls
====
Quick urls description. Should be replaced with OpenAPI spec.

All urls must be prefixed with you dev server url and **`/api/v0.1/`**.
If you use django's `runserver` command with default setting, example url would be **127.0.0.1:8000/api/v0.1/courses/1**


* **'/'**

  Redirects to 'courses/'

* **'courses/'**

  See all courses and POST a new one if registered user.
  To add subject use nested object "subject": {"title": subj_title}.

* **'courses/<int:pk>/'**

  see courses detail and update one if owner

* **'courses/<int:pk>/modules/'**

  see modules in course and POST new ones if owner

* **'courses/<int:pk>/add_teacher/'**

  add new teacher to the course with POST data={'user_pk': int}

* **'items/<int:pk>/'**

  Read, update, delete single item


* **'modules/<int:pk>/'**

  Read, update, delete single module. Nested items are not writable. Use returned `items_url` instead.

* **'modules/<int:pk>/items/'**

  List all items in module. Add new item with POST request, possibly with nested contents.

* **'subjects/'**

  View all subjects and create a new if superuser.


* **'subjects/<slug:pk>/'**

  View one subject and edit it if superuser.


* **'contents/<str:content_type>/<int:pk>/'**

  Delete or update single content

There are also some accounts urls available:

* **'api/v0.1/ accounts/register/'**

* **'api/v0.1/ accounts/login/**

* **'api/v0.1/ accounts/logout/**

Other accounts urls might work but haven't been tested.
