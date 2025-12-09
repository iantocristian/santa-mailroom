# 🎅 Santa's Mailroom - User Guide

Welcome to Santa's Mailroom! This app helps parents manage their children's letters to Santa while keeping the magic alive. Here's everything you need to know.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Adding Your Children](#adding-your-children)
3. [How Letters Work](#how-letters-work)
4. [Managing the Wishlist](#managing-the-wishlist)
5. [Santa's Automatic Replies](#santas-automatic-replies)
6. [Parental Controls](#parental-controls)
7. [Good Deeds Tracker](#good-deeds-tracker)
8. [Settings & Privacy](#settings--privacy)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Step 1: Create Your Account

1. Go to the registration page and enter your email and password
2. You'll need an **invite token** to register (ask the admin Cristian Ianto on slack for one)
3. Once registered, a family is automatically created for you

### Step 2: Set Up Your Santa Email

The app uses a dedicated email address `santaclausgotmail@gmail.com` to receive letters from your children. 

Your children will write to this email address, and Santa will reply automatically!

---

## 👧 Adding Your Children

### From the Dashboard
1. Click **"+ Add Child"** in the top right of the children section
2. Or click **"Add Your First Child"** if you haven't added any yet

### Required Information
- **Name**: Your child's first name (used in Santa's replies)
- **Email**: The email address your child will send letters FROM
  - This is how we match incoming letters to the right child
  - It's securely hashed - we don't store the actual email

### Optional Information
- **Country**: Helps with product pricing in local currency
- **Birth Year**: Santa adjusts his language based on the child's age

### Tips
- Each child needs a unique email address
- Can be a parent's email with a "+" alias (e.g., `parent+emma@gmail.com`)
- The email is only used for matching, not for sending

---

## ✉️ How Letters Work

### Writing to Santa

1. Your child writes an email to the Santa email address you configured
2. They can write anything - wishes, stories, questions!
3. Example subjects: "My Christmas List", "Dear Santa", "Hi Santa!"

### Behind the Scenes

When a letter arrives, the app automatically:

1. **Matches** the sender email to one of your children
2. **Extracts** any gift wishes mentioned in the letter
3. **Checks** for concerning content (parental alerts if needed)
4. **Searches** for product info and pricing
5. **Generates** a personalized reply from Santa
6. **Sends** the reply back to your child!

### Viewing Letters

Go to **Letters** in the sidebar to see:
- All letters received, sorted by date
- Filter by child or year
- Click any letter to read the full content
- See Santa's reply and extracted wishes

---

## 🎁 Managing the Wishlist

### Viewing Wishes

Go to **Wishlist** in the sidebar to see all extracted gift wishes.

Each wish card shows:
- **Product name**: What the child asked for
- **Category**: Toys, Books, Electronics, etc.
- **Price estimate**: Current market price (when available)
- **Status**: Pending, Approved, Denied, or Purchased

### Filtering

- **By Child**: See wishes from a specific child
- **By Status**: Filter to pending, approved, denied, or purchased

### Managing Wish Status

Use the dropdown on each wish to change status:

| Status | Meaning |
|--------|---------|
| ⏳ Pending | Not yet reviewed |
| ✅ Approved | You plan to get this |
| ❌ Denied | Won't be getting this |
| 🎁 Purchased | Already bought! |

### Denied Items

When you deny an item, you can add a reason. Santa's future replies will gently redirect away from this item without mentioning it directly.

### Budget Tracking

The header shows your total estimated budget for approved and purchased items.

---

## 🎅 Santa's Automatic Replies

### How Replies Work

Santa's replies are generated using AI and personalized for each child:

- Uses the child's **name** throughout
- References **specific things** from their letter
- Adjusts **language** based on age
- Mentions **completed good deeds** (with praise!)
- Suggests **new good deeds** to do
- Handles **denied items** gracefully (redirects, doesn't mention)

### Reply Timing

Replies are typically sent within minutes of receiving a letter.

### Example Reply

> *Ho ho ho, Emma!*
>
> *Santa was so happy to receive your wonderful letter! My elves told me about the LEGO castle you mentioned - what a great choice!*
>
> *Mrs. Claus and I were so proud to hear that you helped mom with the dishes last week. That's exactly the kind of kindness that makes Christmas magic!*
>
> *This week, could you try drawing a special card for someone you love? It would mean so much to them!*
>
> *Keep being the wonderful girl you are!*
>
> *With love and jingle bells,*
> *🎅 Santa Claus*

---

## ⚠️ Parental Controls

### Content Moderation

Every letter is automatically scanned for concerning content:

| Flag Type | What It Detects |
|-----------|-----------------|
| Sadness | Depression, loneliness mentions |
| Anxiety | Worry, fear, stress |
| Bullying | Being bullied or bullying others |
| Family Issues | Divorce, fighting, family stress |
| Self-harm | Any concerning mentions |

### Moderation Strictness

Set in **Settings**:
- **Low**: Only flags serious concerns
- **Medium**: Flags moderate emotional content (recommended)
- **High**: Flags any hint of struggle

### Notifications

When content is flagged, you'll receive:
- A notification on the dashboard
- An alert banner with "Review Now" button
- Access to the full context in the Moderation page

### Reviewing Flags

Go to **Moderation** to:
- See all flagged content
- Read the concerning excerpt
- Mark as reviewed with notes
- Take appropriate action

---

## ⭐ Good Deeds Tracker

### How It Works

Santa suggests good deeds in every reply. Track them here!

### Suggested Deeds

Each deed is age-appropriate:
- "Help set the table for dinner"
- "Draw a picture for someone you love"
- "Give a compliment to a friend"
- "Help a parent without being asked"

### Tracking Progress

1. Go to **Good Deeds** in the sidebar
2. See all suggested deeds per child
3. Mark deeds as **completed** when done
4. Add a note about how it went!

### Recognition

When a child completes a deed:
- It's acknowledged in Santa's next reply!
- Builds excitement and positive reinforcement

---

## ⚙️ Settings & Privacy

### Family Settings

Go to **Settings** to configure:

#### Family Information
- **Family Name**: How your family is identified
- **Timezone**: For accurate timing

#### Budget Alerts
- **Alert Threshold**: Get notified when wishlist exceeds this amount

#### Content Moderation
- **Strictness Level**: Low, Medium, or High

#### Data & Privacy
- **Data Retention**: How long to keep data (years)

### Email Privacy

- Child emails are **hashed** (SHA-256)
- We never store the actual email address
- Only you and Santa know who's who!

### Data Retention

Choose how long to keep data:
- Letters, wishes, and deeds are preserved for the scrapbook
- Old data is automatically cleaned up based on your setting

---

## 🔧 Troubleshooting

### Letters Not Appearing

1. **Check the email address** - must exactly match what you registered
2. **Wait a minute** - letters are processed every 60 seconds
3. **Check spam** - your email provider might filter the incoming email

### Santa's Reply Not Arriving

1. **Check spam/junk** - replies might be filtered
2. **Verify SMTP settings** - ensure the mail server is configured
3. **Check the Letters page** - see if the reply was generated

### Wishes Not Extracted

Sometimes AI misses wishes if they're:
- Written very casually ("maybe a bike?")
- In a complex sentence
- Using unusual phrasing

You can manually note these from the letter view.

### Product Prices Missing

Price search uses web search and may not find:
- Very specific items
- Handmade or custom items
- Very new products

Prices are estimates - always verify before purchasing!

---

## 📱 Quick Reference

| Page | Purpose |
|------|---------|
| 🎅 Dashboard | Overview of children, stats, notifications |
| 👧 Children | Add and manage children profiles |
| 🎁 Wishlist | Review and manage gift wishes |
| ✉️ Letters | Read all letters and Santa's replies |
| ⭐ Good Deeds | Track suggested and completed deeds |
| ⚠️ Moderation | Review flagged content |
| ⚙️ Settings | Configure family preferences |

---

## 💡 Tips for Parents

1. **Set up early** - Add children before they start writing letters
2. **Use unique emails** - Gmail aliases work great (`you+childname@gmail.com`)
3. **Review regularly** - Check the moderation page for any flags
4. **Engage with deeds** - Help children complete their good deeds
5. **Save the scrapbook** - Letters make wonderful keepsakes!

---

## 🎄 Making the Magic Last

This app is designed to:
- Keep the **Santa magic alive** for your children
- Give you **parental insight** into their wishes and feelings
- Create **lasting memories** with saved letters
- Encourage **positive behavior** through good deeds
- Provide **peace of mind** with content moderation

Enjoy the magic of Christmas! 🎅🎄✨
