# Project Context

project: doordash-fifty-alert
mode: production
version: 1.7.1

## Current State
- All systems operational
- 86 subscribers
- Both workflows running (check_scores, send_alert)
- Worker deployed with error handling

## Last Session: 2026-01-31
- Code review completed
- Fixed promo window time bug
- Added worker error handling
- Deployed v1.7.1

## Pending Improvements
- CORS restriction (MEDIUM)
- Email validation regex (MEDIUM)
- Deduplicate safe_print() (MEDIUM)
- Pin dependencies (LOW)
