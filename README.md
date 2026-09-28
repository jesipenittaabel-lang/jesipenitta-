# PocketSmart AI

PocketSmart AI is a FastAPI-based generative AI budget
planning assistant.

It provides:

- User registration
- User login
- Logout
- Authentication
- JWT-style access tokens
- Home Interior Planner
- Party Budget Planner
- Jewelry Planner
- Optional jewelry outfit image upload
- Gemini AI integration
- Local fallback recommendations
- Recommendation history
- SQLite database
- Responsive web interface
- FastAPI API documentation

---

## Project Architecture

```text
Browser
   |
   v
Jinja2 HTML + CSS + JavaScript
   |
   v
FastAPI
   |
   +----------------+
   |                |
   v                v
Authentication   Planners
   |                |
   v                v
SQLite        Recommendation Service
                    |
             +------+------+
             |             |
             v             v
          Gemini       Local Catalog
             |
             v
        Recommendations