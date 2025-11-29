# API

## `POST /login`
Description: Log in using credentials
Content-Type: application/json
body:
```json
{"username":"logan","password":"pwd"}
```
returns: JWT token

## `GET /me`
Description: Get info of logged in user
Authorization: Bearer
returns: User model

## `GET /my-calendar`
Description: Get calendar of logged in user
Authorization: Bearer
returns: Calendar model

## `GET /images/<day>`
Description: Get image associated with calendar day=<day>
Authorization: Bearer
returns: binary of image

## `POST /register` (admin-only)
Description: Register a new user
Authorization: Bearer
Content-Type: application/json
body:
```json
{"username":"logan","password":"pwd","name":"Logan","calendar_id":1,"is_admin":"false"}
```
returns: created User

## `POST /calendars` (admin-only)
Description: Add a new calendar
Authorization: Bearer
Content-Type: multipart/form-data
form:
```
name=New Calendar
images=@/path/to/zip/archive
```
returns: created Calendar

## `GET /calendars/<id>` (admin-only)
Description: Get calendar with id=<id>
Authorization: Bearer
returns: Calendar model
