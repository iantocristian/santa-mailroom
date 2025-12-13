# Santa's Mailroom Frontend 🎅

React dashboard for parents to manage children's letters to Santa.

## Setup

```bash
npm install
npm run dev
```

The app runs at http://localhost:5173

## Features

- 🏠 **Dashboard** - Overview with stats, children cards, notifications
- 👧 **Children** - Add/edit children profiles with email matching
- 🎁 **Wishlist** - View extracted wishes with prices, approve/deny items
- ✉️ **Letters** - Read all letters and Santa's replies
- 📖 **Scrapbook** - Timeline view grouped by Christmas year
- ⭐ **Good Deeds** - Track and complete good deeds
- 📤 **Sent Emails** - View all Santa's outgoing emails
- ⚙️ **Settings** - Family preferences, moderation strictness

## Tech Stack

- React 18 + TypeScript
- Vite for build tooling
- Zustand for state management
- React Router for navigation
- Axios for API calls

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Stats and overview |
| Children | `/children` | Manage children profiles |
| Wishlist | `/wishlist` | Gift wishes with filters |
| Letters | `/letters` | All letters and replies |
| Scrapbook | `/timeline` | Year-by-year timeline |
| Good Deeds | `/deeds` | Deed tracker |
| Sent Emails | `/sent-emails` | All Santa's emails |
| Settings | `/settings` | Family config |

## Project Structure

```
src/
├── api/           # Axios client
├── components/    # Shared components (Sidebar, Snowfall)
├── pages/         # Route pages
├── store/         # Zustand state stores
├── styles/        # CSS (Christmas theme)
└── types/         # TypeScript interfaces
```

## Theme

- 🌙 Dark cozy winter night aesthetic
- ❄️ Animated snowfall effect
- 🔴🟢🟡 Christmas color palette (red, green, gold)
- ✨ Festive glow effects
- 📱 Fully responsive
