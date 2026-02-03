# Project Context

project: doordash-fifty-alert
mode: production
version: 1.8.0

## Current State
- All systems operational
- 86 subscribers
- Both workflows running (check_scores, send_alert)
- Worker deployed with error handling

## Promo Details (Updated Feb 2026)
- **Discount:** $5 off (was 50% up to $10)
- **Code:** NBA50
- **Min order:** $15+
- **Requirements:** DashPass members, delivery only, 1 use per account
- **Season ends:** April 12, 2026

## Last Session: 2026-02-02
- Updated promo rules (DoorDash nerfed from 50% to $5)
- Updated email template with new messaging
- Updated landing page with new promo details
- Updated config with promo constants

## Pending Improvements
- CORS restriction (MEDIUM)
- Email validation regex (MEDIUM)
- Deduplicate safe_print() (MEDIUM)
- Pin dependencies (LOW)
