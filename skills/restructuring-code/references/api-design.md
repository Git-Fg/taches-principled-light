# API Design

Standards for REST API contract design, resource modeling, and versioning.

## Resource Modeling

Design URLs as nouns representing resources, not verbs representing operations.

**Rules:**
- Use nouns, not verbs: `/users` not `getUsers` or `createUser`
- Proper hierarchy: `/users/{id}/posts` for nested resources
- Idempotency where appropriate: `PUT /users/{id}` for updates
- Avoid deep nesting: flatten when nesting exceeds 2 levels

**Examples:**
```
/users              GET (list), POST (create)
/users/{id}         GET, PUT, DELETE
/users/{id}/posts   GET (user's posts)
/posts/{id}/author GET (single relation)
```

## HTTP Semantics

Match HTTP methods to their semantic meaning.

| Method | Semantics | Idempotent | Safe |
|--------|-----------|------------|------|
| GET | Read resource | Yes | Yes |
| POST | Create new resource | No | No |
| PUT | Full replace | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

**Status Code Rules:**
- 2xx: Success (200 OK, 201 Created, 204 No Content)
- 4xx: Client error (400 Bad Request, 404 Not Found, 409 Conflict)
- 5xx: Server error (500 Internal Server Error)

Never return 200 with an error body. Never return 404 with a 2xx status.

## Breaking Changes

A breaking change requires a version bump.

**Breaking changes:**
- Removing or renaming fields in response
- Changing field types
- Adding required request fields
- Changing URL structure
- Removing endpoints
- Changing error response format

**Non-breaking changes:**
- Adding optional request fields
- Adding new fields to response
- Adding new endpoints

## Versioning Strategies

**URL versioning** (explicit, cache-friendly):
```
/v1/users
/v2/users
```
Simple but pollutes URL space.

**Header versioning** (clean URLs, requires client awareness):
```
Accept: application/vnd.api+json;version=1
```
URLs stay clean; clients control version via headers.

**Deprecation pattern:**
```
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## Response Shapes

**Error format consistency:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [{ "field": "email", "issue": "invalid format" }]
  }
}
```

**Pagination patterns:**
```json
{
  "data": [...],
  "pagination": {
    "cursor": "abc123",
    "hasMore": true
  }
}
```

## Anti-Patterns

- Verb-based endpoints: `POST /createUser`, `GET /getUserById`
- Status code misuse: 200 OK with error body, 404 with 2xx
- Inconsistent error format across endpoints
- Breaking changes without version bump
- PUT without idempotency guarantees
- GET with side effects (logging is OK; persistence is not)

## API Checklist

- [ ] Endpoints use nouns, not verbs
- [ ] HTTP methods match semantics (GET=read, POST=create, etc.)
- [ ] Status codes match semantics (2xx for success, 4xx/5xx for errors)
- [ ] Consistent error format across all endpoints
- [ ] Breaking changes planned for versioning
- [ ] Pagination uses consistent pattern
