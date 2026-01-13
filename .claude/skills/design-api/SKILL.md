---
name: design-api
description: API design workflow defining endpoints, designing schemas, documenting with OpenAPI, generating clients, and creating tests for REST/GraphQL/gRPC
allowed-tools:
  - Read
  - Write
  - Bash
---

# Design API Skill

Comprehensive API design workflow for REST, GraphQL, and gRPC APIs. See full REST API OpenAPI specification patterns in documentation.

## Quick Reference

**REST Best Practices**:
- Use nouns for resources (`/users`, not `/getUsers`)
- HTTP methods: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove)
- Status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found)
- Versioning: `/api/v1/users`
- Pagination: Cursor-based recommended
- Rate limiting: Standard headers

**GraphQL Best Practices**:
- Schema-first design
- Nullable by default, use `!` for required
- Pagination: Relay cursor connections
- Error handling: Use `errors` array

**gRPC Best Practices**:
- Protocol Buffers for schema
- Streaming for real-time data
- Service definitions with RPC methods
- Error handling with status codes

For complete examples and templates, see OpenAPI specifications and GraphQL schema examples.
