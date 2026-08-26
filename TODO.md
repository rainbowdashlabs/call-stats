# Frontend TODO

## Bugs

### ~~TimePicker: inverted min/max on seconds~~ DONE
### ~~MemberQualifications: broken SmartSelect binding~~ DONE
### ~~Exercise interfaces: members/instructors typed as singular instead of array~~ DONE
### ~~DatePicker one-way binding in exercise forms~~ DONE
### ~~listExercises/listYouthExercises: wrong HTTP method and return types~~ DONE
### ~~MemberView: retirement date displayed as raw unix timestamp~~ DONE
### ~~CreateExercise watcher: parameters swapped~~ DONE

---

## Code quality

### ~~Remove console.log statements~~ DONE
### ~~Remove dead code in Theme.vue~~ DONE

---

## Missing features

### ~~No exercise list views~~ DONE (added ExerciseList and YouthExerciseList components with pagination)

### ~~No statistics/reports page~~ DONE (backend endpoints + vue-echarts StatisticsView with year/rolling days/date range/member filters)

### ~~No call editing~~ DONE (inline editing of note and abort_reason in CallView)

### ~~No delete confirmation on CallView~~ DONE

### ~~No 404/catch-all route~~ DONE

### ~~Member detail: no activity history~~ DONE (MemberActivity component with year stats + call list)

### ~~No loading/empty states~~ DONE (added to CallList, MembersView, MemberQualifications)

### ~~No form validation before submission~~ DONE (added canSubmit computed + disabled buttons)

---

## UX improvements

### ~~CallView datetime order is confusing~~ DONE

### ~~No success feedback after create actions~~ DONE (SuccessPopup with auto-dismiss + emitSuccess calls)

### ~~CallList: redundant @change handler~~ DONE

### ~~Submit buttons lack disabled state during requests~~ DONE (submitting ref + disabled binding)

## ~~Minimal user management~~ DONE
Two accounts (admin/member) configured via `ADMIN_PASSWORD`, `MEMBER_PASSWORD`, `TOKEN_SECRET` env vars.
- Backend: token-based auth, all endpoints require authentication, login at `/api/auth/login`
- Frontend: login page, route guards, admin-only UI hidden for member role

## ~~Dockerfile~~ DONE
- Multi-stage `Dockerfile` at project root (Node build + Python runtime)
- `compose.yml` for local dev (backend hot-reload + PostgreSQL)
- `compose.prod.yml` for deployment (built image + PostgreSQL)
- `.github/workflows/build-and-publish.yml` — builds and pushes to GHCR on push to main/tags
- `.dockerignore` for clean builds
- FastAPI serves the built frontend SPA in production (no separate web server needed)