# Flask Authentication Service with JWT and OAuth2
This Flask-based authentication service utilizes JSON Web Tokens (JWT) to securely authenticate users and OAuth2 for authorization. It uses Redis to store invalidated access tokens, providing an added layer of security by ensuring that only valid tokens are accepted for access. The service is designed for scalability and can handle high traffic, with built-in support for handling multiple users and user roles. The authentication service is built with security and performance in mind, providing a fast and reliable way to authenticate and authorize users in any application. It follows OAuth2 protocol for authorization and allows users to grant third-party applications access to their resources without sharing their credentials. 

## Features
- JSON Web Token (JWT) based authentication
- OAuth2 protocol for authorization
- Redis storage for invalidated access tokens
- Scalable and high-performance design
- Support for multiple user roles
- Secure password hashing and storage
- RESTful endpoints for easy integration with other systems
- Advanced security feature like rate-limiting
- Advanced error handling and exception management

## Project initialization

1. Create a `.env.prod` file and populate it. Use `.env.prod.example` as an example.
2. Run Docker containers: 
```console
make up
```
3. Run migrations: 
```console
make migrate
```

4. Create superuser:
```console
make createsuperuser
```

## API
The API is available at:
- $HOST/auth/api/


The API is available at:
- $HOST/movies/api/
