# 🔐 Auth Practice

**A full-stack authentication and authorization learning project built with Angular, FastAPI, PostgreSQL, and Docker.**

Auth Practice is a hands-on project designed to explore secure authentication, role-based authorization, and modern web application security following OWASP best practices.

The goal is to build a realistic authentication system from scratch before integrating similar security features into larger applications.

> **Project Status:** 🚧 V1.0.0 — Planning & Initial Setup

## 🎯 Project Objectives

- Understand authentication vs. authorization.
- Build secure registration, login, and logout workflows.
- Implement JWT access tokens and refresh token rotation.
- Apply role-based access control (RBAC).
- Secure passwords using Argon2 hashing.
- Protect frontend routes and backend API endpoints.
- Understand Angular HTTP interceptors and route guards.
- Practice OWASP security recommendations.
- Implement automated security and integration tests.
- Practice professional GitHub workflows using Issues, Projects, and Pull Requests.

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Angular, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| Migrations | Alembic |
| Authentication | JWT, OAuth2 Bearer Token |
| Password Security | Argon2 |
| Infrastructure | Docker, Docker Compose |
| Backend Testing | Pytest, HTTPX |
| Frontend Testing | Angular Testing Utilities |
| CI/CD | GitHub Actions |
| Project Management | GitHub Projects |

## 🏗️ Architecture

The application follows a modular architecture with clear separation between the frontend, backend, and database.

```text
                ┌──────────────────┐
                │ Angular Frontend │
                │   TypeScript     │
                └────────┬─────────┘
                         │
                    HTTP / REST
                         │
                ┌────────▼─────────┐
                │   FastAPI API    │
                │                  │
                │ Authentication   │
                │ Authorization    │
                │ Business Logic   │
                └────────┬─────────┘
                         │
                    SQLAlchemy
                         │
                ┌────────▼─────────┐
                │   PostgreSQL     │
                │     Docker       │
                └──────────────────┘
```

## 📁 Planned Project Structure

```text
auth-practice/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   └── src/
│       └── app/
│           ├── core/
│           │   ├── guards/
│           │   ├── interceptors/
│           │   └── services/
│           ├── features/
│           │   ├── auth/
│           │   ├── dashboard/
│           │   └── admin/
│           └── shared/
│
├── docs/
│   ├── architecture/
│   ├── database/
│   └── security/
│
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

*The directory structure may evolve during implementation.*

## 🔑 Planned Features

### Authentication

- User registration
- Login and logout
- Secure password hashing
- JWT access tokens
- Refresh token rotation
- Session revocation
- Current-user endpoint
- Protected API endpoints

### Authorization

- Role-based access control (RBAC)
- User and Admin roles
- Backend permission enforcement
- Angular route guards
- Unauthorized access handling

### Angular Security

- Reactive login and registration forms
- Authentication state management using Angular Signals
- HTTP interceptors
- Protected routes
- Automatic session refresh
- Secure error handling

### Security Best Practices

Security measures will follow relevant recommendations from the OWASP Cheat Sheet Series.

- Password hashing with Argon2
- Short-lived access tokens
- Secure refresh token cookies
- CSRF protection where applicable
- Server-side input validation
- Secure CORS configuration
- Login rate limiting
- Least-privilege authorization
- No secrets committed to Git
- Authentication and authorization tests

> Angular route guards improve navigation and user experience, but backend authorization remains mandatory. Sensitive access decisions must always be enforced by FastAPI.

## 🗄️ Database Design

The initial database design will include:

| Entity | Responsibility |
|---|---|
| Users | Store user accounts and password hashes |
| Roles | Define application roles |
| User Roles | Associate users with roles |
| Refresh Sessions | Manage refresh token sessions and revocation |

The Entity Relationship Diagram (ERD) will be documented in `docs/database/`.

## 🗺️ Development Roadmap

### Phase 1 — Project Setup
- [ ] Initialize GitHub repository
- [x] Create GitHub Project board
- [ ] Initialize Angular application
- [ ] Initialize FastAPI backend
- [ ] Configure PostgreSQL using Docker Compose

### Phase 2 — Database & Architecture
- [ ] Design ER diagram
- [ ] Implement SQLAlchemy models
- [ ] Configure Alembic migrations
- [ ] Implement database connection

### Phase 3 — Backend Authentication
- [ ] Implement user registration
- [ ] Implement login
- [ ] Implement password hashing
- [ ] Generate and validate JWTs
- [ ] Implement refresh token rotation
- [ ] Implement logout and session revocation

### Phase 4 — Angular Authentication
- [ ] Build login and registration pages
- [ ] Implement AuthService
- [ ] Manage authentication state using Signals
- [ ] Implement HTTP interceptors
- [ ] Implement authentication route guards
- [ ] Build protected dashboard

### Phase 5 — Authorization & Security
- [ ] Implement role-based permissions
- [ ] Implement admin-only API endpoints
- [ ] Implement authorization guards
- [ ] Configure secure cookies and CSRF protection
- [ ] Implement rate limiting
- [ ] Test OWASP-related security scenarios

### Phase 6 — Testing & Release
- [ ] Write backend authentication tests
- [ ] Write authorization tests
- [ ] Write Angular tests
- [ ] Configure GitHub Actions
- [ ] Complete documentation
- [ ] Release V1.0.0

## 📋 Project Management

Development is organized through GitHub Projects using a Kanban workflow.

**[View GitHub Project — Auth Practice Development](https://github.com/users/mustafataha5/projects/6)**

Workflow:

`Backlog → Ready → In Progress → In Review → Done`

Each development task will be tracked through a GitHub Issue and implemented in a dedicated Git branch.

Example branch names:

```text
chore/initial-project-setup
feat/backend-registration
feat/backend-login
feat/jwt-authentication
feat/angular-login
feat/role-based-access
test/auth-security
```

## 📚 Learning Resources

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

## 👨‍💻 Author

**Mustafa Taha**

Full-Stack Developer | Data & AI Engineer

GitHub: [@mustafataha5](https://github.com/mustafataha5)

---

**Auth Practice** — Learning secure full-stack application development through practical implementation.
