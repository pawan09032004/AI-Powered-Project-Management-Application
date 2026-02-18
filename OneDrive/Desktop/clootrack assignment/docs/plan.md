### Project Plan & Staged Checklist

This document maps each stage (0–9) to:
- A clear checklist of work items.
- The corresponding **git commit message** to use at the end of the stage.

---

### Stage 0 – Environment & Repo Sanity Check

- [x] Verify project directory and presence of `Tech_Intern_Assessment.pdf`.
- [x] Add a small helper to extract PDF text if needed.
- [x] Create initial `docs/` structure (`requirements.md`, `plan.md`, `testing.md`).
- [x] Confirm git repository status and avoid committing unrelated user-home files.

**Planned commit message:** `chore: initialize repository and tooling`

---

### Stage 1 – Requirement Understanding

- [x] Read `Tech_Intern_Assessment.pdf` carefully.
- [x] Extract and summarize:
  - Core problem.
  - Inputs & outputs.
  - Required features (backend, frontend, LLM, Docker).
  - Constraints and evaluation criteria.
- [x] Write the summary into `docs/requirements.md`.

**Planned commit message:** `docs: add detailed requirements and acceptance criteria`

---

### Stage 2 – Solution Design & High-Level Structure

- [ ] Define high-level architecture:
  - Django + DRF backend (`backend/`).
  - React frontend (`frontend/`).
  - PostgreSQL via Docker.
  - LLM integration service/module inside the backend.
- [ ] Design API layout and URL structure (`/api/tickets/`, `/api/tickets/stats/`, `/api/tickets/classify/`).
- [ ] Decide on LLM provider abstraction and error-handling strategy.
- [ ] Plan Docker Compose services and environment variables (DB, backend, frontend, LLM API key).
- [ ] Break down implementation work per stage (3–9) with a short description.
- [ ] Record all of the above in this `docs/plan.md`.

**Planned commit message:** `feat: add high-level solution design and project structure plan`

---

### Stage 3 – Project Skeleton & Boilerplate

- [ ] Create Django project in `backend/` with:
  - Ticket app (e.g., `tickets`).
  - Basic settings for PostgreSQL, DRF, CORS, and environment-based configuration.
- [ ] Create React app in `frontend/` (e.g., Vite or CRA).
- [ ] Add base layout and routing (Ticket Form, Ticket List, Stats Dashboard views).
- [ ] Add `docker-compose.yml` with services:
  - `db` (PostgreSQL).
  - `backend` (Django).
  - `frontend` (React).
- [ ] Add top-level `README.md` skeleton describing the project and how to run it.

**Planned commit message:** `feat: scaffold project structure and base modules`

---

### Stage 4 – Core Functionality (Iteration 1)

- [ ] Implement Ticket model in Django with all required fields and DB-level constraints.
- [ ] Implement DRF serializers and viewsets for:
  - `POST /api/tickets/`.
  - `GET /api/tickets/` (newest first, with filters and search).
  - `PATCH /api/tickets/<id>/`.
- [ ] Wire up URL routes and basic pagination.
- [ ] Implement minimal tests for:
  - Model constraints.
  - Ticket creation and listing.
  - Basic filtering/search behaviour.

**Planned commit message:** `feat: implement core ticket API with basic tests`

---

### Stage 5 – Remaining Features & Edge Cases

- [ ] Implement `/api/tickets/stats/` using DB aggregations (no Python for-loops).
- [ ] Implement `/api/tickets/classify/` endpoint:
  - Calls an LLM client abstraction.
  - Validates and normalizes LLM output.
  - Handles errors gracefully with sensible fallbacks.
- [ ] Implement LLM client module with:
  - Configurable provider (via environment variables).
  - Clear prompt text embedded in code.
  - Robust error handling and logging (without leaking secrets).
- [ ] Add tests for:
  - Stats endpoint correctness.
  - Classify endpoint success and failure paths.

**Planned commit message:** `feat: add remaining features and handle edge cases`

---

### Stage 6 – Evaluation, Testing & Validation

- [ ] Expand backend test suite:
  - Additional filter + search combinations.
  - Edge cases around invalid inputs and status transitions.
- [ ] Add basic frontend tests if time allows (e.g., for core components or hooks).
- [ ] Manually verify:
  - Ticket creation, listing, filtering, search.
  - Stats dashboard data.
  - LLM classify flow and failure handling.
- [ ] Record test scenarios and outcomes in `docs/testing.md`.

**Planned commit message:** `test: improve coverage and document validation results`

---

### Stage 7 – Documentation & Usage Guide

- [ ] Flesh out `README.md` with:
  - Project overview.
  - Tech stack.
  - Setup instructions (local + Docker).
  - LLM provider choice and rationale.
  - Key design decisions.
- [ ] Add short architecture overview (diagram or text) describing:
  - How frontend, backend, DB, and LLM interact.
  - Main data flows (ticket creation, listing, stats, classify).
- [ ] Link to important docs in `docs/` (requirements, plan, testing log).

**Planned commit message:** `docs: add usage guide and architecture overview`

---

### Stage 8 – Refactoring & Polish

- [ ] Review backend code for:
  - Repeated logic that can be extracted into helpers/services.
  - Clear naming and separation of concerns.
  - Removal of dead code and debug prints.
- [ ] Review frontend code for:
  - Component reuse.
  - Cleaner state management and prop drilling reductions.
  - Consistent styling and error handling.
- [ ] Run formatters/linters where available.

**Planned commit message:** `refactor: clean up code and improve readability`

---

### Stage 9 – Final Review & Packaging

- [ ] Run `docker-compose up --build` to ensure the full stack works end-to-end.
- [ ] Verify `.env` / environment variable instructions are accurate and safe (no secrets committed).
- [ ] Double-check docs (`README.md`, `docs/requirements.md`, `docs/plan.md`, `docs/testing.md`) for clarity.
- [ ] Ensure git history is clean, with one commit per stage and descriptive messages.
- [ ] Prepare final zip including `.git` directory and all project files.

**Planned commit message:** `chore: finalize project for submission`


