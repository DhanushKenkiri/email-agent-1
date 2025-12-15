# Cold Outreach Email AI Agent 🎯

**One API call. Three AI agents. Zero spam vibes.**

An autonomous agent that researches a company, writes personalized cold emails, and quality-checks them before you hit send. Built for the [Masumi](https://masumi.network) agent marketplace. Listed on Sokosumi.

[![API Status](https://img.shields.io/badge/API-v1.0.0-green)](/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)

---

## 🔥 Why This Exists

Cold emails suck. Not because the concept is flawed, but because:

1. **Generic templates get ignored** — "I noticed you work at {company_name}" isn't personalization
2. **Research takes forever** — 15 minutes per prospect, just to find something relevant
3. **Spam filters are smart** — They've seen every "touching base" and "quick question" trick
4. **Copywriting is hard** — Most devs (including me) write emails that sound like robots

This agent exists to fix all four. You provide company info, it does deep research, writes emails that sound human, and checks for spam triggers. All in one API call.

---

## 🤖 What This Agent Actually Does

| Step | Agent | What Happens |
|------|-------|--------------|
| 1 | **Web Scraper** | Fetches and parses the target company's website |
| 2 | **Research Agent** | Extracts industry, value prop, recent news, personalization hooks |
| 3 | **Copy Agent** | Writes 3 subject lines + primary email + follow-up email |
| 4 | **QA Agent** | Analyzes for spam risk (low/medium/high) — does NOT rewrite |

**Output:** Structured JSON with everything you need. No chat, no fluff, no "As an AI language model..."

---

## 🧠 How the Agent Thinks (Core Logic)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         YOUR INPUT                                    │
│  { company_name, company_website, target_role, product, goal, tone } │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        WEB SCRAPER                                    │
│  • Fetches website HTML                                              │
│  • Strips nav, footer, scripts                                       │
│  • Extracts readable text (first 8000 chars)                         │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      RESEARCH AGENT                                   │
│  Prompt: "Analyze this company for cold outreach..."                 │
│  Output: { industry, value_prop, recent_news, personalization_hooks }│
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        COPY AGENT                                     │
│  Prompt: "Write cold emails using this research..."                  │
│  Output: { subject_lines[3], primary_email, follow_up_email }        │
│  Enforces: No spam words, no emojis, tone matching                   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         QA AGENT                                      │
│  Prompt: "Analyze spam risk, DO NOT rewrite..."                      │
│  Output: { spam_risk_score: "low" | "medium" | "high" }              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        FINAL OUTPUT                                   │
│  { subject_lines, primary_email, follow_up_email,                    │
│    personalization_points, spam_risk_score }                         │
└──────────────────────────────────────────────────────────────────────┘
```

Sequential execution. No parallelism. No race conditions. Boring and reliable.

---

## 📋 API Contract

### `POST /run` — Generate Outreach Emails

**Request Body:**
```json
{
  "company_name": "Stripe",
  "company_website": "https://stripe.com",
  "target_role": "Head of Growth",
  "product_description": "AI-powered B2B onboarding tool that reduces time-to-value by 60%",
  "outreach_goal": "Book a 15-minute intro call",
  "tone": "professional"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `company_name` | string | ✅ | The target company |
| `company_website` | string (URL) | ✅ | Must be valid HTTP/HTTPS URL |
| `target_role` | string | ✅ | Who you're emailing |
| `product_description` | string | ✅ | What you're selling (be specific) |
| `outreach_goal` | string | ✅ | What you want them to do |
| `tone` | string | ✅ | `professional`, `casual`, or `founder` |

**Response (200 OK):**
```json
{
  "subject_lines": [
    "Cutting onboarding time at Stripe",
    "Quick question about Stripe's B2B flow",
    "For the Head of Growth at Stripe"
  ],
  "primary_email": "Hi [Name],\n\nI noticed Stripe recently expanded into...",
  "follow_up_email": "Hi [Name],\n\nWanted to follow up on my note...",
  "personalization_points": [
    "Recent expansion into embedded finance",
    "Developer-first documentation approach",
    "Active hiring for growth roles"
  ],
  "spam_risk_score": "low"
}
```

### `GET /health` — Health Check

Returns `{"status": "ok", "service": "cold-outreach-agent", "version": "1.0.0"}` if alive.

### `GET /docs` — Swagger UI

Interactive API documentation. Try it in browser.

---

## ❌ Failure Modes

Yes, things can go wrong. Here's what and why:

| Code | Error | What Happened | Your Move |
|------|-------|---------------|-----------|
| `400` | `validation_error` | Your input JSON is malformed or missing fields | Check the schema, all fields are required |
| `502` | `scrape_failed` | Couldn't fetch the company website | Is the URL correct? Site might block bots or be down |
| `500` | `internal_error` | LLM call failed or returned unparseable response | Retry. If persistent, check API key/quota |
| `500` | `llm_timeout` | Model took too long to respond | Retry. Happens occasionally during high load |

**The honest truth:** If the target website is heavily JavaScript-rendered (SPA), scraping might get minimal content. We grab what we can.

---

## 🛠️ Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | FastAPI | Async, fast, auto-generates OpenAPI docs |
| **Validation** | Pydantic v2 | Strict typing, great error messages |
| **LLM** | Google Gemini | Fast, cheap, good enough for structured output |
| **Scraping** | httpx + BeautifulSoup | Async HTTP + reliable HTML parsing |
| **Deployment** | Railway | One-click deploy, handles everything |

**Why not LangChain/CrewAI?** Tried it. Too much abstraction for a simple sequential pipeline. Direct LLM calls are easier to debug.

---

## 🚀 Setup & Run Locally

### Prerequisites

- Python 3.10+ (3.11 recommended)
- Gemini API key ([get one free](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone and enter
cd agent-service

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Set your API key
set GEMINI_API_KEY=your-key-here      # Windows
export GEMINI_API_KEY=your-key-here   # macOS/Linux

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
🚀 Cold Outreach Agent is alive and ready to write emails
📖 Docs available at /docs
```

Visit **http://localhost:8000/docs** to test.

### Deploy to Railway

```bash
# Push to GitHub, then:
# 1. Create new Railway project
# 2. Connect your repo
# 3. Add environment variable: GEMINI_API_KEY=your-key
# 4. Railway auto-deploys on push
```

Railway detects Python, installs deps, runs uvicorn. No Dockerfile needed.

---

## 💰 Rate Limits & Cost Reality

### Gemini Free Tier
- **15 requests/minute** (per model)
- **1,500 requests/day**
- **1M tokens/minute**

For most use cases, free tier is enough. If you're doing bulk outreach (100+ prospects/day), you'll need a paid tier.

### Estimated Cost (Paid Tier)
- ~3 LLM calls per `/run` request
- ~2,000 tokens per call
- **Cost per email generation: ~$0.001-0.002**

You can generate ~500 personalized email sets for roughly $1.

---

## 📝 Example Run (Realistic)

**Input:**
```json
{
  "company_name": "Linear",
  "company_website": "https://linear.app",
  "target_role": "Head of Product",
  "product_description": "AI copilot for product managers that auto-generates PRDs from user feedback",
  "outreach_goal": "Get feedback on our beta",
  "tone": "founder"
}
```

**Output:**
```json
{
  "subject_lines": [
    "Fellow builder - quick product question",
    "Saw Linear's approach to issue tracking",
    "From one PM tool maker to another"
  ],
  "primary_email": "Hey,\n\nI've been using Linear for our team and honestly, the speed is unreal. You clearly obsess over the details.\n\nI'm building something adjacent — an AI copilot that helps PMs turn scattered user feedback into structured PRDs. Still early, but the pattern recognition is getting scary good.\n\nWould love your take on the approach. Not a sales pitch — genuinely curious if this resonates with how you think about the PM workflow.\n\n15 minutes if you're open to it?",
  "follow_up_email": "Hey,\n\nFloating this back up. I know the inbox is brutal.\n\nShort version: AI that watches your feedback channels and drafts PRDs. The \"why now\" is that LLMs finally got good enough to understand product context.\n\nHappy to share a 2-min demo video if that's easier than a call.",
  "personalization_points": [
    "Linear's focus on speed and keyboard-first UX",
    "Their opinionated approach to project management",
    "Recent Series B and scaling challenges"
  ],
  "spam_risk_score": "low"
}
```

Notice: `founder` tone is more casual, more direct, acknowledges shared builder experience.

---

## 🗺️ Roadmap

### v1.0 (Current)
- ✅ Research → Copy → QA pipeline
- ✅ Three tone options
- ✅ Spam risk scoring
- ✅ Structured JSON output

### v1.1 (Next)
- [ ] LinkedIn profile scraping (for recipient personalization)
- [ ] Multi-email sequence generation (3-5 touch campaign)
- [ ] A/B subject line variants with confidence scores

### v1.2 (Future)
- [ ] CRM integration hooks (HubSpot, Salesforce)
- [ ] Email sending integration (via SendGrid/Resend)
- [ ] Response tracking and optimization feedback loop

### v2.0 (Dream)
- [ ] Full autonomous prospecting: give it an ICP, it finds leads and writes emails
- [ ] Multi-agent negotiation for copy refinement
- [ ] Learn from your sent email performance

---

## 💭 Philosophy

This agent is opinionated. It doesn't try to be everything to everyone. It writes cold emails — one specific thing, done well. The research is real (scraped, not hallucinated). The copy follows proven patterns (no gimmicks). The QA is honest (it won't tell you an email is great if it isn't).

Most AI tools try to impress you with creativity. This one tries to get you replies.

---

## License

MIT — do whatever you want with it.

---

*Built by a developer who was tired of writing cold emails. Now an AI does it instead.*
