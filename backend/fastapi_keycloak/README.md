# Fastapi Keyclaok boilerplate

This boilerplate uses fastapi with keycloak.

It provides basic authentication via jwt access token

## Endpoints

### users
GET `/api/v1/users/all`
GET `/api/v1/users/{user_id}`
PUT `/api/v1/users/{user_id}`
POST `/api/v1/users`

### auth
POST `api/v1/auth/register`
- Register a user
POST `api/v1/auth/login/access-token`
- Get the JWT Acess Token with PS512 Algorithm
GET `api/v1/auth/me`
- Get the current users informations