# Santa's Mailroom - Implementation Walkthrough

## Overview

A complete platform where children email Santa with their wish lists, and parents manage everything through a festive dashboard with snowfall animation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Email Pipeline                               │
├─────────────────────────────────────────────────────────────────┤
│ POP3 Fetcher → PostgreSQL Jobs → Worker → GPT → SMTP Sender    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
├─────────────────────────────────────────────────────────────────┤
│ Auth | Children | Wishlist | Letters | Deeds | Sent Emails     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    React Dashboard                               │
├─────────────────────────────────────────────────────────────────┤
│ Dashboard | Wishlist | Scrapbook | Good Deeds | Sent Emails    │
└─────────────────────────────────────────────────────────────────┘
```

> Uses PostgreSQL polling queue instead of Celery/Redis for simplicity.

---

## Backend Implementation

### Database Models

| Model | Purpose |
|-------|---------|
| `User` | Parent accounts with auth |
| `Family` | Tenant with settings |
| `Child` | Registered children (hashed emails) |
| `Letter` | Incoming emails |
| `WishItem` | Extracted items with pricing |
| `SantaReply` | Generated replies |
| `GoodDeed` | Kindness tracking |
| `ModerationFlag` | Content safety alerts |
| `SentEmail` | All outgoing emails |

### API Routers

| Router | Endpoints |
|--------|-----------|
| `auth.py` | Login, register, current user |
| `family.py` | Family CRUD, stats |
| `children.py` | Child management |
| `wishlist.py` | Items, filtering, status updates |
| `letters.py` | Letters, timeline view |
| `deeds.py` | Good deeds with email triggers |
| `sent_emails.py` | View all outgoing emails |
| `notifications.py` | Parent alerts |

### Services

| Service | Purpose |
|---------|---------|
| `email_service.py` | POP3 fetch, SMTP send (SSL/TLS) |
| `gpt_service.py` | Extraction, moderation, reply generation, deed emails |
| `product_search_service.py` | OpenAI web search for products |
| `notification_service.py` | Parent alerts |

### Worker Jobs

| Job | Trigger | Action |
|-----|---------|--------|
| `fetch_emails` | Scheduled (60s) | Check POP3 inbox |
| `process_letter` | New letter | Extract, moderate, search, reply |
| `send_reply` | Reply ready | Send via SMTP |
| `send_deed_email` | Deed created | Email child about new deed |
| `send_deed_congrats` | Deed completed | Email child congratulations |

---

## Frontend Implementation

### Christmas Theme

- 🌙 Dark winter night background
- ❄️ Animated snowfall component
- 🔴🟢🟡 Christmas color palette
- ✨ Festive glow effects
- 📱 Responsive design

### Pages

| Page | Route | Features |
|------|-------|----------|
| Dashboard | `/` | Stats, children cards, notifications |
| Children | `/children` | Add/edit with country dropdown |
| Wishlist | `/wishlist` | Filter by child/status, budget total |
| Letters | `/letters` | List/detail view with replies |
| Scrapbook | `/timeline` | Timeline grouped by year |
| Good Deeds | `/deeds` | Add, complete (triggers email!) |
| Sent Emails | `/sent-emails` | View all Santa emails |
| Settings | `/settings` | Family preferences |

### Zustand Stores

| Store | State |
|-------|-------|
| `authStore` | User auth, tokens |
| `familyStore` | Family data, stats |
| `childrenStore` | Children list |
| `wishlistStore` | Wish items |
| `lettersStore` | Letters |
| `deedsStore` | Good deeds |
| `notificationsStore` | Alerts |

---

## Key Features Implemented

### Good Deeds Flow
1. Parent adds deed → Santa emails child about it
2. Child does the deed → Parent marks complete
3. System sends congratulations email from Santa

### Email Tracking
All Santa emails are recorded in `sent_emails` table:
- Letter replies
- Deed suggestions
- Deed congratulations

### Product Search
Uses OpenAI Responses API with web search tool to find real product prices.

### Currency Support
Prices display in local currency based on child's country.

---

## What's Left

- [ ] Moderation dashboard (placeholder only)
- [ ] PDF export for scrapbook
- [ ] Push notifications
- [ ] Link deed emails to thread (reply detection)
