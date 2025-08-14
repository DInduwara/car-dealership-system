# Car Dealership Backend (Django + DRF + PostgreSQL)

A production-ready backend implementing authentication (JWT), role-based permissions, inventory, bookings with overlap prevention, sales with commission, and Celery notifications.

## Tech
- Django 4, DRF, SimpleJWT
- PostgreSQL (SQLite fallback for local), Redis + Celery
- django-filter, cors-headers

## Quickstart (local)
1. Create and fill `.env` from `.env.example`.
2. Install system prerequisites (Python 3.11+, virtualenv):
   - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y python3-venv python3-dev build-essential libpq-dev redis-server`
3. Create venv and install deps:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Migrate and run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
5. Start Celery (optional):
   ```bash
   celery -A dealership worker -l info
   ```

## Apps and Endpoints
- Auth
  - POST `/api/auth/register/`
  - POST `/api/auth/login/` (JWT obtain)
  - POST `/api/auth/refresh/`
- Cars
  - GET `/api/cars/` (filters: make, model, year, min_price, max_price, fuel_type, body_type, transmission)
  - GET `/api/cars/{id}/`
  - POST `/api/cars/` (ADMIN/SALES)
  - PUT/PATCH `/api/cars/{id}/`
  - POST `/api/cars/{id}/photos/`
  - DELETE `/api/cars/{id}/photos/{photo_id}/`
  - GET `/api/cars/{id}/available-slots/?date=YYYY-MM-DD`
- Bookings
  - POST `/api/bookings/` (customer)
  - GET `/api/bookings/me/` (customer)
  - PATCH `/api/bookings/{id}/approve|decline|complete|cancel|no-show/` (staff/admin)
- Sales
  - POST `/api/sales/` (staff/admin)
  - GET `/api/sales/`
  - GET `/api/sales/{id}/`
- Staff
  - POST `/api/staff/`
  - GET `/api/staff/`
  - PATCH `/api/staff/{id}/`
  - GET `/api/staff/{id}/metrics/`

## Frontend (DriveWise UI)

A Django-rendered frontend is provided in the `frontend` app with templates and static files. Run the server:

```
python manage.py runserver 0.0.0.0:8000
```

UI is served at `/` and API under `/api/`.

## Notes
- Custom user with roles: ADMIN, SALES, CUSTOMER.
- Booking rules: 1-hour, starts 09:00–16:00, overlap prevention per car.
- On sale: mark car SOLD, cancel future bookings, update staff metrics, create commission.
- Car photos: ordered, enforce single primary.

## Implementation Notes (Backend Integration)
- Auth
  - POST `/api/auth/register/` { full_name, email, phone, password, accept_terms } -> creates CUSTOMER only
  - POST `/api/auth/login/` { username, password } -> { access, refresh, user { id, role, name, email, phone } }
  - GET/PATCH `/api/auth/me/` -> current user profile
  - POST `/api/auth/password/forgot/` and `/api/auth/password/reset?token=` placeholders
- Cars
  - GET `/api/cars/` supports search, filter, ordering, pagination
  - GET `/api/cars/{id}/`
  - GET `/api/cars/{id}/available-slots?date=YYYY-MM-DD` -> { slots: [{startAt, endAt}] }
  - POST `/api/cars/` (ADMIN/SALES), PATCH `/api/cars/{id}/`, DELETE `/api/cars/{id}/`
  - POST `/api/cars/{id}/photos/` multipart (s3_key, alt_text)
- Bookings
  - POST `/api/bookings/` { car, start_at } -> creates 1hr booking, prevents overlap
  - GET `/api/bookings/me/` customer’s bookings
  - PATCH `/api/bookings/{id}/reschedule` { start_at }
  - PATCH `/api/bookings/{id}/cancel-mine`
  - Admin/Staff: list and actions approve/decline/complete/no-show
- Staff
  - POST `/api/staff/` (ADMIN) to create STAFF/ADMIN
  - GET `/api/staff/{id}/metrics/`
- Sales
  - CRUD `/api/sales/` (ADMIN/SALES)

Rules
- Test drive duration exactly 1 hour; start 09:00–16:00 showroom local time
- Prevent overlapping bookings per car; SOLD/REMOVED cars not bookable
- Public sign-up only creates CUSTOMER; STAFF via admin only

## QA Checklist
- [ ] Sign Up restricts to CUSTOMER; requires Terms checkbox; success toast/message.
- [ ] Login returns token and role; role-based redirect and nav visible.
- [ ] Forgot/Reset password pages work with placeholders.
- [ ] Car listing has search, filters, sort, pagination stub, clear filters.
- [ ] Car detail shows gallery/specs/price; Book Test Drive with date + hourly slots (09:00–16:00) and conflict handling toasts.
- [ ] My Bookings page: list + calendar toggle; reschedule/cancel actions enforced by status.
- [ ] Admin Dashboard shows quick actions (sticky) with keyboard hints and metrics stubs.
- [ ] Admin Cars page supports add/edit/delete, bulk mark sold, export CSV; CSV import UI only.
- [ ] Admin Bookings actions: Approve/Decline/Complete/No-Show.
- [ ] Admin Staff pages: list, add new via form; metrics drawer.
- [ ] Admin Sales page: filters + export CSV.
- [ ] Legal pages linked in footer and referenced in signup.
- [ ] Accessibility: labels, ARIA attributes, keyboard actions on slots, modals focusable.
- [ ] Toasters for success/error; skeletons/spinners stubs.
- [ ] Responsive layout maintains DriveWise spacing and typography.