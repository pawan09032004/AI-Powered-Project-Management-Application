### Stage 1 Checklist – Requirement Understanding

- [x] Carefully read `Tech_Intern_Assessment.pdf`
- [x] Identify core problem, inputs/outputs, and required features
- [x] Capture constraints and evaluation criteria
- [x] Document everything clearly in this file

---

### Core Problem

Build a full-stack **Support Ticket System** where users can:
- Submit support tickets describing their issue.
- See existing tickets, filter them, and search them.
- View aggregated statistics about tickets.

The twist is an **LLM-powered assistant**: when a user writes a ticket description, the system calls an LLM
to **auto-suggest a category and priority**, which the user can then accept or override before submitting.
The entire system (backend, frontend, and database) must be fully containerized and runnable via Docker Compose.

---

### Inputs & Outputs

- **Ticket creation input (user-facing form)**
  - `title` (short summary of the issue)
  - `description` (free-text, full problem description)
  - `category` (one of: `billing`, `technical`, `account`, `general`)
  - `priority` (one of: `low`, `medium`, `high`, `critical`)
  - `status` is not provided by the user on creation; it defaults to `open`.

- **Backend ticket model fields (database level)**
  - `title`: `CharField(max_length=200)`, **required**.
  - `description`: `TextField`, **required**.
  - `category`: `CharField` with choices `billing`, `technical`, `account`, `general`,
    values **must be constrained at the DB level**.
  - `priority`: `CharField` with choices `low`, `medium`, `high`, `critical`,
    values **must be constrained at the DB level**.
  - `status`: `CharField` with choices `open`, `in_progress`, `resolved`, `closed`,
    defaults to `open`, constrained at the DB level.
  - `created_at`: `DateTimeField`, auto-set on creation.

- **API endpoints and their inputs/outputs**
  - `POST /api/tickets/`
    - **Input**: JSON body with ticket fields (`title`, `description`, `category`, `priority`, optional `status`).
    - **Output**: Created ticket JSON and HTTP **201** status on success.
  - `GET /api/tickets/`
    - **Input (query params)**:
      - `?category=...`
      - `?priority=...`
      - `?status=...`
      - `?search=...` (searches in `title` and `description`)
      - Filters are **combinable**.
    - **Output**: Paginated list (or plain list) of tickets ordered by newest first.
  - `PATCH /api/tickets/<id>/`
    - **Input**: JSON body with fields to update (e.g., `status`, `category`, `priority`).
    - **Output**: Updated ticket JSON.
  - `GET /api/tickets/stats/`
    - **Input**: No body; may accept optional query params if useful, but not required by the spec.
    - **Output**: JSON with the following structure:
      ```json
      {
        "total_tickets": 124,
        "open_tickets": 67,
        "avg_tickets_per_day": 8.3,
        "priority_breakdown": {
          "low": 30, "medium": 52, "high": 31, "critical": 11
        },
        "category_breakdown": {
          "billing": 28, "technical": 55, "account": 22, "general": 19
        }
      }
      ```
  - `POST /api/tickets/classify/`
    - **Input**: JSON body with a `description` field.
    - **Output**:
      ```json
      {
        "suggested_category": "...",
        "suggested_priority": "..."
      }
      ```

---

### Required Features

- **Backend**
  - Django + Django REST Framework + PostgreSQL.
  - Ticket model with all fields and DB-level constraints as described above.
  - REST API endpoints:
    - `POST /api/tickets/` (create ticket).
    - `GET /api/tickets/` (list tickets, newest first, with combined filters and search).
    - `PATCH /api/tickets/<id>/` (partial updates such as status/overrides).
    - `GET /api/tickets/stats/` (aggregated stats).
    - `POST /api/tickets/classify/` (LLM-based suggestions).
  - Stats endpoint must compute:
    - Total number of tickets.
    - Number of open tickets.
    - Average tickets per day.
    - Breakdown by priority.
    - Breakdown by category.
    - **All using database aggregations, not Python-level loops.**

- **LLM Integration**
  - A classification service that:
    - Accepts a ticket description.
    - Calls an LLM with a prompt asking for a **category** and **priority**.
    - Returns suggested `category` and `priority` in a strict JSON shape.
  - Exposed via `POST /api/tickets/classify/`.
  - LLM API key must be provided via an **environment variable defined in `docker-compose.yml`**.
  - Must handle failures gracefully:
    - If the LLM is unavailable or returns invalid data:
      - The system should not crash.
      - Ticket submission should still be possible (e.g., fallback to reasonable defaults or require manual user input).
  - The **prompt text** used to call the LLM must be **included in the codebase** for review.

- **Frontend (React)**
  1. **Ticket Creation Form**
     - Fields: `title`, `description`, `category`, `priority`.
     - Category and Priority dropdowns should be **pre-filled by the LLM suggestion**
       after the user enters a description, but remain fully editable.
     - A "Classify" behavior that calls `/api/tickets/classify/`, shows a loading state,
       and updates dropdowns when suggestions arrive.
     - Submit button that POSTs to `/api/tickets/`.
     - After successful submission:
       - Clear the form.
       - Show the new ticket in the list **without a full page reload**.
  2. **Ticket List**
     - Shows all tickets, newest first.
     - Filters for `category`, `priority`, and `status`.
     - Search bar that filters by `title` and `description` via `?search=`.
  3. **Stats Dashboard**
     - Fetches data from `/api/tickets/stats/`.
     - Displays: total tickets, open count, average per day, and breakdowns by priority and category.
     - Automatically refreshes stats when a new ticket is submitted.
  - Styling is secondary; correctness, usability, and clean state management are primary.

- **Docker & Infrastructure**
  - A `docker-compose.yml` that brings up:
    - **PostgreSQL** database service.
    - **Django backend** service (runs migrations automatically on startup).
    - **React frontend** service.
  - Proper `depends_on` / health-waiting so that services start in a sensible order.
  - LLM API key passed into the backend via an environment variable.
  - The full app should be runnable end-to-end with:
    - `docker-compose up --build`
    - (LLM features depend on a valid API key set by the reviewer).

---

### Constraints & Evaluation Criteria

- **Time limit**
  - Approximately **3 hours** from receiving the assessment (practically, we will still structure the work cleanly in stages).

- **Technical stack constraints**
  - Backend: **Django + DRF + PostgreSQL**.
  - Frontend: **React**.
  - Infrastructure: **Docker + Docker Compose**.
  - LLM: any provider is acceptable, but:
    - API key **must not be hardcoded**.
    - Must be configurable via environment variables.

- **Key evaluation areas**
  - **End-to-end functionality (20%)**
    - `docker-compose up --build` works and the app runs fully.
  - **LLM integration (20%)**
    - Correctness of `/api/tickets/classify/`.
    - Prompt quality and robustness.
    - Graceful error handling and good UX around suggestions.
  - **Data modeling (10%)**
    - Correct field types.
    - Choices and constraints enforced at the **database** level.
  - **API design (10%)**
    - Clean, RESTful endpoints.
    - Proper HTTP status codes.
    - Working filters and search.
  - **Query logic (10%)**
    - Efficient use of database aggregation for stats (no Python loops).
  - **React structure (10%)**
    - Sensible component structure and state management.
    - Clean API integration.
  - **Code quality (10%)**
    - Readable, consistent code.
    - No dead code or leftover debug prints.
  - **Commit history (5%)**
    - Incremental, meaningful commits that reflect the development process.
  - **README (5%)**
    - Clear setup instructions.
    - Explanation of chosen LLM and why.
    - Key design decisions.

- **Submission rules**
  - Submit a **zip of the entire project folder**, including:
    - The `.git` directory (for commit history review).
    - A working `docker-compose.yml`.
    - A `README.md` with setup instructions, LLM choice, and design notes.
  - Do **not** push the project to a public repository.
  - You may use documentation and learning resources, but the commit history should clearly reflect **your own** work.


