# Cold Outreach Email AI Agent — Specification

> AKA "the thing that writes emails so you don't have to"

## 1. Problem Statement

Sales teams waste **hours** researching prospects and writing personalized cold emails that often land in spam folders or get ignored. There's no consistency, personalization is usually shallow ("I love what you're doing at [COMPANY]" — we've all seen it), and quality control is basically vibes-based.

**This agent fixes that.** It automates the entire pipeline — from company research to copy generation to spam risk checking — and delivers production-ready emails in seconds.

Will it replace your best sales rep? No. Will it save your mediocre ones 3 hours a day? Absolutely.

---

## 2. Agent Responsibilities

We've got a crew of three agents. They work in sequence, no freelancing allowed.

| Agent | What It Actually Does |
|-------|----------------------|
| **ResearchAgent** | Scrapes the company website, figures out what they do, finds stuff we can reference to not sound generic |
| **CopyAgent** | Takes the research and writes actual emails — 3 subject lines, 1 primary email, 1 follow-up |
| **QAAgent** | Reads the emails and tells us if they're gonna land in spam (spoiler: sometimes they are) |

**The flow (no exceptions):**
```
ResearchAgent → CopyAgent → QAAgent → You get emails
```

---

## 3. Input JSON Schema

Here's what you send us. Miss a field and Pydantic will yell at you.

```json
{
  "company_name": "string (required)",
  "company_website": "HttpUrl (required)",
  "target_role": "string (required)",
  "product_description": "string (required)",
  "outreach_goal": "string (required)",
  "tone": "Literal['professional', 'casual', 'founder'] (required)"
}
```

### What each field means (in case it wasn't obvious)

| Field | Type | What We Need | Example |
|-------|------|--------------|---------|
| `company_name` | string | The company you're targeting | "Acme Corp" |
| `company_website` | HttpUrl | Their homepage (we scrape this) | "https://acme.com" |
| `target_role` | string | Who you're emailing | "VP of Engineering" |
| `product_description` | string | What you're selling, in plain English | "AI-powered code review tool" |
| `outreach_goal` | string | What you want them to do | "Book a 15-min demo call" |
| `tone` | Literal | Pick one: professional, casual, or founder | "professional" |

---

## 4. Output JSON Schema

Here's what you get back. Every time. No surprises.

```json
{
  "subject_lines": ["string", "string", "string"],
  "primary_email": "string",
  "follow_up_email": "string",
  "personalization_points": ["string"],
  "spam_risk_score": "Literal['low', 'medium', 'high']"
}
```

### The fine print

| Field | Type | Rules |
|-------|------|-------|
| `subject_lines` | List[str] | Always exactly 3 — for A/B testing like grown-ups |
| `primary_email` | string | Max 120 words, no emojis, no exclamation marks |
| `follow_up_email` | string | Same rules, different angle |
| `personalization_points` | List[str] | 1-5 things we found about the company |
| `spam_risk_score` | Literal | "low" = you're good, "high" = maybe rewrite |

---

## 5. Error Cases

Things will go wrong. Here's how we tell you about it.

| Code | Error | What Happened | Our Response |
|------|-------|---------------|--------------|
| `400` | `validation_error` | You sent garbage input | `{"error": "validation_error", "details": [...]}` |
| `422` | `missing_field` | You forgot a required field | `{"error": "missing_field", "field": "..."}` |
| `502` | `scrape_failed` | We couldn't reach the website | `{"error": "scrape_failed", "message": "..."}` |
| `500` | `agent_error` | The AI had a moment | `{"error": "agent_error", "message": "..."}` |
| `504` | `timeout` | Took too long (>60s) | `{"error": "timeout", "message": "..."}` |

---

**Stuff we're NOT doing** (so don't ask):

- ❌ Sending emails — we write them, you send them
- ❌ CRM integration — that's your job
- ❌ Email tracking/analytics — use Mailtrack or something
- ❌ A/B testing logic — we give you options, you pick
- ❌ Managing email threads — this is cold outreach, not Gmail
- ❌ Any kind of UI — API only, deal with it
- ❌ User auth — Masumi handles that layer
- ❌ Storing data — stateless, we forget everything

---

## 7. Success Criteria

Before we ship, all of these must be true:

- [x] All inputs validated before agent runs
- [x] Output matches schema exactly (no extra fields sneaking in)
- [x] Emails have zero emojis and zero exclamation marks
- [x] QA agent actually evaluates spam risk independently
- [x] Response time under 30 seconds for normal requests
- [x] Flow is deterministic: Research → Copy → QA (no shortcuts)

If any of these fail, Masumi rejects us. So they better not fail.k
- [ ] Response time < 30 seconds for typical request
- [ ] Deterministic flow: Research → Copy → QA
