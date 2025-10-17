# Full-Stack • Intermediate • 90-Min Exercise — Shipments Management + CSV Import

**Timebox:** 90 minutes. Do as much as you can; leave notes under "Trade-offs & Next Steps".

> This repo includes boilerplate and comments that outline expectations and requirements. Please follow them and keep scope tight.

## What's Provided
- FastAPI backend with MongoDB
- Next.js frontend with Redux Toolkit
- Docker Compose setup
- Boilerplate for shipments API and UI

## Problem Statement
Build a shipments management system with multi-criteria filtering, cursor pagination, inline quantity editing with transactions, and CSV import functionality. The system should handle facilities, shipments, and shipment items with proper data relationships and atomic updates.

## Tasks (Must-have)
1. Backend: GET /shipments with filters (status, facilityId, from/to dates, PO number) + cursor pagination
2. Backend: PATCH /shipments/{id}/items for bulk quantity updates (use transactions)
3. Backend: POST /shipments/import to parse and import CSV file
4. Backend: Add indexes on facilityId, status, createdAt
5. Frontend: Shipments table with multi-filter UI
6. Frontend: Inline edit for item quantities with optimistic updates
7. Frontend: CSV file upload with parsing feedback

## Expected Solution (Checklist)
- Correct API contracts/state handling.
- Pagination implemented (cursor).
- Error/loading/empty states.
- Basic a11y (labels, keyboard access).
- Reasonable structure & naming.
- Atomic bulk updates via transactions.
- CSV parsing with validation.

## Bonus (If time permits)
- Export shipments to CSV
- Shipment status workflow validation
- Drag-and-drop CSV upload
- Real-time upload progress

## Clone & Run

```bash
git clone https://github.com/yourorg/fs-intermediate-shipments
cd fs-intermediate-shipments

# Start MongoDB (with replica set for transactions)
docker compose up -d

# Start backend
cd server
cp .env.example .env
pip install -r requirements.txt
python app/seed/seed.py
uvicorn app.main:app --reload --port 4000

# Start frontend
cd client
pnpm i
cp .env.example .env
pnpm dev
```

## Submission

Push your work to a branch named `{your-name}` and update this README with:
- Run steps, assumptions, trade-offs, next steps.
- Transaction handling approach.
- CSV parsing strategy.

---

© 2025 yourorg – For interview use only.

