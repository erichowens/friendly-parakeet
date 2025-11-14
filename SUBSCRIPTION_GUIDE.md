# 💳 Friendly Parakeet AI Subscription Service

## Overview

Friendly Parakeet now offers a secure server-side AI subscription service for users who don't have (or don't want to manage) their own OpenAI API keys. This provides a seamless, secure way to access AI features with simple monthly billing.

## 🏗️ Architecture

### Components

1. **Backend API** (`server/app.py`)
   - FastAPI-based REST API
   - JWT authentication with refresh tokens
   - PostgreSQL for user data
   - Redis for caching and rate limiting
   - Stripe for payment processing
   - OpenAI API integration

2. **Subscription Manager** (`src/parakeet/subscription_manager.py`)
   - Client-side subscription handling
   - Secure token storage using keyring
   - API communication layer
   - Usage tracking cache

3. **Menu Bar Integration** (`src/parakeet/menubar_app.py`)
   - Subscription menu UI
   - Login/signup flows
   - Usage monitoring display
   - Plan management

## 💰 Pricing Tiers

| Tier | Price | Monthly Requests | Features |
|------|-------|-----------------|----------|
| **Free** | $0 | 10 | Basic AI completion |
| **Friendly** | $4.99 | 500 | + Brilliant Budgie ideas, Priority support |
| **Professional** | $9.99 | 2000 | + GPT-4 access, Custom prompts |
| **Team** | $19.99 | Unlimited | + Team collaboration, API access |

### Why These Prices?

- **Cost Analysis**: OpenAI API costs ~$0.002 per 1k tokens
- **Average request**: ~500-1000 tokens = $0.001-0.002
- **Margin**: 60-70% after API costs
- **Infrastructure**: ~$50-100/month for hosting
- **Break-even**: ~15 Friendly subscribers

## 🚀 Deployment Guide

### Prerequisites

1. **Accounts needed**:
   - Stripe account for payments
   - OpenAI API key
   - Railway/Render/Fly.io for hosting
   - PostgreSQL database
   - Redis instance

### Step 1: Set up Stripe

1. Create a Stripe account at https://stripe.com
2. Create products and prices:
```bash
# Using Stripe CLI
stripe products create --name="Friendly Parakeet Friendly" --description="500 AI requests per month"
stripe prices create --product=PRODUCT_ID --currency=usd --unit-amount=499 --recurring-interval=month
```
3. Save the price IDs for environment variables

### Step 2: Deploy Backend

#### Option A: Railway (Recommended)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Initialize project:
```bash
cd server
railway login
railway init
```
3. Add services:
```bash
railway add postgresql
railway add redis
```
4. Set environment variables:
```bash
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set STRIPE_SECRET_KEY=sk_live_...
railway variables set STRIPE_WEBHOOK_SECRET=whsec_...
railway variables set OPENAI_API_KEY=sk-...
# Add price IDs
railway variables set STRIPE_PRICE_FRIENDLY=price_...
railway variables set STRIPE_PRICE_PRO=price_...
railway variables set STRIPE_PRICE_TEAM=price_...
```
5. Deploy:
```bash
railway up
```

#### Option B: Docker Compose (Self-hosted)

1. Clone and configure:
```bash
cd server
cp .env.example .env
# Edit .env with your keys
```
2. Run:
```bash
docker-compose up -d
```

#### Option C: Render

1. Connect GitHub repo
2. Create Web Service
3. Add PostgreSQL and Redis
4. Set environment variables
5. Deploy

### Step 3: Configure Client

Update the API URL in `subscription_manager.py`:
```python
self.api_base_url = "https://your-api-url.railway.app"
```

### Step 4: Database Setup

Run migrations:
```bash
# SSH into your deployment
python -c "from app import engine, Base; import asyncio; asyncio.run(Base.metadata.create_all(bind=engine))"
```

## 🔒 Security Features

1. **Authentication**
   - JWT tokens with short expiry
   - Refresh token rotation
   - Secure password hashing (bcrypt)

2. **API Security**
   - Rate limiting per tier
   - Request validation
   - CORS configuration
   - HTTPS only

3. **Payment Security**
   - Stripe handles all payment data
   - No credit cards stored
   - Webhook signature verification

4. **Token Storage**
   - macOS Keychain for tokens
   - Never stored in plain text
   - Automatic cleanup on logout

## 📊 Usage Tracking

### How It Works

1. Each API request decrements monthly quota
2. Usage resets on monthly anniversary
3. Real-time usage display in menu bar
4. Warning notifications at 80% usage

### Rate Limits

- Free: 10/hour
- Friendly: 100/hour
- Professional: 500/hour
- Team: 1000/hour

## 🧪 Testing

### Local Development

1. Run backend locally:
```bash
cd server
pip install -r requirements.txt
uvicorn app:app --reload
```

2. Use test Stripe keys:
```bash
export STRIPE_SECRET_KEY=sk_test_...
```

3. Test with curl:
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# Get AI completion
curl -X POST http://localhost:8000/ai/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, AI!"}'
```

## 💡 Brilliant Budgies with Subscription

Paid subscribers get enhanced Brilliant Budgie ideas:

- **Free**: No Brilliant Budgie access
- **Friendly**: Basic ideas with GPT-3.5
- **Professional**: Advanced ideas with longer context
- **Team**: Premium ideas with GPT-4

## 📈 Monitoring

### Metrics to Track

1. **User Metrics**
   - Signups per day
   - Conversion rate (free → paid)
   - Churn rate
   - Active users

2. **Usage Metrics**
   - Requests per user
   - Token usage
   - API costs
   - Error rates

3. **Revenue Metrics**
   - MRR (Monthly Recurring Revenue)
   - ARPU (Average Revenue Per User)
   - LTV (Lifetime Value)

### Monitoring Tools

- Sentry for error tracking
- Prometheus + Grafana for metrics
- Stripe Dashboard for payments
- PostgreSQL analytics queries

## 🆘 Troubleshooting

### Common Issues

1. **"Not authenticated" error**
   - Token expired → Re-login
   - Token missing → Check keyring

2. **"Rate limit exceeded"**
   - Wait for reset
   - Upgrade plan

3. **"Payment failed"**
   - Check Stripe logs
   - Verify webhook configuration

4. **High latency**
   - Check Redis connection
   - Monitor database performance
   - Consider caching

## 🚦 Launch Checklist

- [ ] Stripe account configured
- [ ] Products and prices created
- [ ] Backend deployed
- [ ] Database initialized
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] Webhook endpoint configured
- [ ] Rate limiting tested
- [ ] Payment flow tested
- [ ] Error handling verified
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Terms of Service prepared
- [ ] Privacy Policy prepared

## 📝 Legal Considerations

1. **Terms of Service**: Define usage limits, acceptable use
2. **Privacy Policy**: Explain data handling
3. **Refund Policy**: Clear cancellation terms
4. **GDPR Compliance**: Data export/deletion
5. **Tax Handling**: Configure Stripe Tax

## 🎯 Marketing Strategy

1. **Free Tier**: Hook users with 10 free requests
2. **Upgrade Prompts**: Show when approaching limits
3. **Feature Gates**: Brilliant Budgies for paid only
4. **Referral Program**: Free month for referrals
5. **Annual Discount**: 2 months free on yearly

## 💰 Revenue Projections

| Subscribers | Friendly | Professional | Team | MRR |
|------------|----------|--------------|------|-----|
| 100 | 70 | 25 | 5 | $749 |
| 500 | 350 | 125 | 25 | $3,745 |
| 1000 | 700 | 250 | 50 | $7,490 |

## 🔮 Future Enhancements

1. **Team Features**
   - Shared usage pool
   - Admin dashboard
   - Usage analytics

2. **Enterprise Plan**
   - Custom limits
   - SLA guarantees
   - Dedicated support

3. **Additional AI Models**
   - Claude API
   - Llama models
   - Custom fine-tuning

4. **Usage Insights**
   - Cost per project
   - AI effectiveness metrics
   - Suggestion quality tracking

---

## Quick Start for Users

1. **Open Friendly Parakeet menu bar app**
2. **Click 💳 Subscription → Sign Up**
3. **Create account with email/password**
4. **Choose a plan** (start with Free!)
5. **Start using AI features!**

No API keys needed - we handle everything securely on our servers! 🦜✨