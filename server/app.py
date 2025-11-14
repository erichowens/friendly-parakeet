"""
Friendly Parakeet AI Subscription Service
Secure server-side AI API for users without local API keys
"""

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import stripe
import openai
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import secrets
from enum import Enum

# Configuration
class Settings(BaseModel):
    # Server
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/parakeet")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_ids: Dict[str, str] = {
        "friendly": os.getenv("STRIPE_PRICE_FRIENDLY", ""),
        "professional": os.getenv("STRIPE_PRICE_PRO", ""),
        "team": os.getenv("STRIPE_PRICE_TEAM", "")
    }

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Rate Limits
    rate_limit_free: str = "10/hour"
    rate_limit_friendly: str = "100/hour"
    rate_limit_professional: str = "500/hour"
    rate_limit_team: str = "1000/hour"

settings = Settings()

# Initialize services
app = FastAPI(
    title="Friendly Parakeet AI Service",
    description="Secure AI subscription service for coding assistance",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "parakeet://*"],  # Mac app custom scheme
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
Base = declarative_base()
engine = create_async_engine(settings.database_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Redis setup for caching and rate limiting
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Stripe setup
stripe.api_key = settings.stripe_secret_key

# OpenAI setup
openai.api_key = settings.openai_api_key


# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Subscription
    stripe_customer_id = Column(String, nullable=True)
    subscription_tier = Column(String, default="free")
    subscription_status = Column(String, default="inactive")
    subscription_end_date = Column(DateTime, nullable=True)

    # Usage tracking
    monthly_usage = Column(Integer, default=0)
    usage_reset_date = Column(DateTime, default=datetime.utcnow)

    # Settings
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    endpoint = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    request_data = Column(JSON, default={})
    response_data = Column(JSON, default={})


# Pydantic Models
class SubscriptionTier(str, Enum):
    FREE = "free"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    TEAM = "team"


class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class SubscriptionRequest(BaseModel):
    tier: SubscriptionTier
    payment_method_id: Optional[str] = None


class AIRequest(BaseModel):
    prompt: str = Field(..., max_length=5000)
    context: Optional[Dict[str, Any]] = {}
    model: str = "gpt-3.5-turbo"
    max_tokens: int = Field(default=500, le=2000)


class BrilliantBudgieRequest(BaseModel):
    project_info: Dict[str, Any]
    request_type: str = Field(..., pattern="^(test|refactor|performance|docs|creative)$")
    custom_instructions: Optional[str] = None


# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    async with async_session() as session:
        user = await session.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

    return user


async def check_usage_limit(user: User) -> bool:
    """Check if user has exceeded their monthly usage limit."""
    # Reset usage if needed
    if datetime.utcnow() > user.usage_reset_date:
        user.monthly_usage = 0
        user.usage_reset_date = datetime.utcnow() + timedelta(days=30)

    limits = {
        "free": 10,
        "friendly": 500,
        "professional": 2000,
        "team": float('inf')
    }

    limit = limits.get(user.subscription_tier, 10)
    return user.monthly_usage < limit


async def track_usage(user: User, tokens: int, cost: float, endpoint: str, request_data: dict, response_data: dict):
    """Track API usage for billing and analytics."""
    async with async_session() as session:
        # Update user usage
        user.monthly_usage += 1

        # Log usage
        usage_log = UsageLog(
            user_id=user.id,
            endpoint=endpoint,
            tokens_used=tokens,
            cost=cost,
            request_data=request_data,
            response_data={"preview": str(response_data)[:500]}  # Truncate response
        )

        session.add(usage_log)
        await session.commit()


# API Endpoints

@app.get("/")
async def root():
    return {
        "service": "Friendly Parakeet AI Service",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Secure AI API access",
            "Subscription management",
            "Usage tracking",
            "Brilliant Budgie ideas"
        ]
    }


@app.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """Create a new user account."""
    async with async_session() as session:
        # Check if user exists
        existing_user = await session.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )

        session.add(new_user)
        await session.commit()

        # Create tokens
        access_token = create_access_token(data={"sub": new_user.username})
        refresh_token = create_refresh_token(data={"sub": new_user.username})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login with username and password."""
    async with async_session() as session:
        user = await session.query(User).filter(User.username == user_data.username).first()

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        # Create tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )


@app.post("/subscription/create")
async def create_subscription(
    request: SubscriptionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create or update a subscription."""
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={"user_id": str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id

        # Get price ID
        price_id = settings.stripe_price_ids.get(request.tier.value)
        if not price_id:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{"price": price_id}],
            payment_method=request.payment_method_id,
            expand=["latest_invoice.payment_intent"]
        )

        # Update user subscription status
        async with async_session() as session:
            current_user.subscription_tier = request.tier.value
            current_user.subscription_status = subscription.status
            current_user.subscription_end_date = datetime.fromtimestamp(
                subscription.current_period_end
            )
            await session.commit()

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subscription/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user)):
    """Cancel the current subscription."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        # Cancel subscription at period end
        subscriptions = stripe.Subscription.list(
            customer=current_user.stripe_customer_id,
            status="active"
        )

        for sub in subscriptions:
            stripe.Subscription.modify(
                sub.id,
                cancel_at_period_end=True
            )

        return {"message": "Subscription will be cancelled at the end of the billing period"}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ai/complete")
@limiter.limit("100/hour")  # Default rate limit
async def ai_complete(
    request: AIRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Get AI completion with usage tracking."""
    # Check usage limit
    if not await check_usage_limit(current_user):
        raise HTTPException(
            status_code=429,
            detail=f"Monthly usage limit exceeded for {current_user.subscription_tier} tier"
        )

    try:
        # Make OpenAI API call
        response = await openai.ChatCompletion.acreate(
            model=request.model,
            messages=[
                {"role": "system", "content": "You are Friendly Parakeet's AI assistant."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=request.max_tokens,
            temperature=0.7
        )

        # Extract response
        completion = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        # Calculate cost (rough estimate)
        cost = tokens_used * 0.000002  # Rough pricing

        # Track usage in background
        background_tasks.add_task(
            track_usage,
            current_user,
            tokens_used,
            cost,
            "/ai/complete",
            request.dict(),
            {"completion": completion}
        )

        return {
            "completion": completion,
            "tokens_used": tokens_used,
            "remaining_quota": await get_remaining_quota(current_user)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@app.post("/ai/brilliant-budgie")
@limiter.limit("50/hour")
async def brilliant_budgie(
    request: BrilliantBudgieRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Generate a Brilliant Budgie idea based on project analysis."""
    # Check if user has access to this feature
    if current_user.subscription_tier == "free":
        raise HTTPException(
            status_code=403,
            detail="Brilliant Budgie ideas require a paid subscription"
        )

    # Check usage limit
    if not await check_usage_limit(current_user):
        raise HTTPException(status_code=429, detail="Monthly usage limit exceeded")

    try:
        # Create specialized prompt for idea generation
        prompt = f"""
        As a Brilliant Budgie, analyze this project and suggest a helpful improvement:

        Project: {request.project_info.get('name', 'Unknown')}
        Type: {request.project_info.get('type', 'Unknown')}
        Language: {request.project_info.get('language', 'Unknown')}
        Recent Activity: {request.project_info.get('recent_activity', 'None')}

        Request Type: {request.request_type}
        Custom Instructions: {request.custom_instructions or 'None'}

        Generate a specific, actionable improvement idea with:
        1. A clear title
        2. Description of the improvement
        3. Implementation steps
        4. Estimated time
        5. Benefits

        Be creative but practical!
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4" if current_user.subscription_tier == "team" else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Brilliant Budgie, an AI that generates helpful coding improvement ideas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.8
        )

        idea = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        # Track usage
        background_tasks.add_task(
            track_usage,
            current_user,
            tokens_used,
            tokens_used * 0.000003,
            "/ai/brilliant-budgie",
            request.dict(),
            {"idea": idea}
        )

        return {
            "idea": idea,
            "type": request.request_type,
            "tokens_used": tokens_used
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brilliant Budgie error: {str(e)}")


@app.get("/user/usage")
async def get_usage_stats(current_user: User = Depends(get_current_user)):
    """Get current usage statistics."""
    async with async_session() as session:
        # Get usage logs for current month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        logs = await session.query(UsageLog).filter(
            UsageLog.user_id == current_user.id,
            UsageLog.timestamp >= month_start
        ).all()

        total_tokens = sum(log.tokens_used for log in logs)
        total_cost = sum(log.cost for log in logs)

        return {
            "subscription_tier": current_user.subscription_tier,
            "monthly_usage": current_user.monthly_usage,
            "monthly_limit": get_monthly_limit(current_user.subscription_tier),
            "total_tokens": total_tokens,
            "estimated_cost": total_cost,
            "usage_reset_date": current_user.usage_reset_date.isoformat(),
            "subscription_status": current_user.subscription_status
        }


async def get_remaining_quota(user: User) -> int:
    """Get remaining API calls for the month."""
    limits = {
        "free": 10,
        "friendly": 500,
        "professional": 2000,
        "team": 999999
    }
    limit = limits.get(user.subscription_tier, 10)
    return max(0, limit - user.monthly_usage)


def get_monthly_limit(tier: str) -> int:
    """Get monthly usage limit for a subscription tier."""
    limits = {
        "free": 10,
        "friendly": 500,
        "professional": 2000,
        "team": 999999
    }
    return limits.get(tier, 10)


@app.post("/webhook/stripe")
async def stripe_webhook(request: dict):
    """Handle Stripe webhook events."""
    # Verify webhook signature
    # Update subscription status based on events
    # This would be implemented with proper Stripe webhook handling
    return {"received": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)