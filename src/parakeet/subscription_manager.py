"""Subscription management for Friendly Parakeet AI features."""

import json
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import keyring
import hashlib


class SubscriptionManager:
    """Manages AI subscription and authentication."""

    def __init__(self, config_dir: Path):
        """Initialize subscription manager.

        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self.config_file = config_dir / "subscription.json"
        self.api_base_url = "https://api.friendlyparakeet.com"  # Change to your deployed URL

        # Use keyring for secure token storage
        self.keyring_service = "friendly_parakeet"
        self.keyring_username = "api_tokens"

        # Load saved config
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=30.0)

    def _load_config(self) -> Dict[str, Any]:
        """Load subscription configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "user": None,
            "subscription_tier": "free",
            "subscription_status": "inactive",
            "usage": {
                "monthly_usage": 0,
                "monthly_limit": 10,
                "reset_date": None
            }
        }

    def _save_config(self):
        """Save subscription configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_stored_tokens(self) -> Optional[Dict[str, str]]:
        """Get stored authentication tokens from keyring."""
        try:
            tokens_json = keyring.get_password(self.keyring_service, self.keyring_username)
            if tokens_json:
                return json.loads(tokens_json)
        except Exception:
            pass
        return None

    def store_tokens(self, access_token: str, refresh_token: str):
        """Store authentication tokens securely."""
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "stored_at": datetime.now().isoformat()
        }
        keyring.set_password(
            self.keyring_service,
            self.keyring_username,
            json.dumps(tokens)
        )

    def clear_tokens(self):
        """Clear stored tokens."""
        try:
            keyring.delete_password(self.keyring_service, self.keyring_username)
        except Exception:
            pass

    async def signup(self, email: str, username: str, password: str) -> Dict[str, Any]:
        """Create a new account.

        Args:
            email: User email
            username: Username
            password: Password

        Returns:
            Response data with tokens
        """
        response = await self.client.post(
            f"{self.api_base_url}/auth/signup",
            json={
                "email": email,
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.store_tokens(data["access_token"], data["refresh_token"])
            self.config["user"] = username
            self._save_config()
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json().get("detail", "Signup failed")}

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to existing account.

        Args:
            username: Username
            password: Password

        Returns:
            Response data with tokens
        """
        response = await self.client.post(
            f"{self.api_base_url}/auth/login",
            json={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.store_tokens(data["access_token"], data["refresh_token"])
            self.config["user"] = username
            self._save_config()
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json().get("detail", "Login failed")}

    async def logout(self):
        """Logout and clear tokens."""
        self.clear_tokens()
        self.config["user"] = None
        self.config["subscription_tier"] = "free"
        self.config["subscription_status"] = "inactive"
        self._save_config()

    async def create_subscription(self, tier: str, payment_method_id: Optional[str] = None) -> Dict[str, Any]:
        """Create or update subscription.

        Args:
            tier: Subscription tier (friendly, professional, team)
            payment_method_id: Stripe payment method ID

        Returns:
            Subscription response
        """
        tokens = self.get_stored_tokens()
        if not tokens:
            return {"success": False, "error": "Not authenticated"}

        response = await self.client.post(
            f"{self.api_base_url}/subscription/create",
            json={
                "tier": tier,
                "payment_method_id": payment_method_id
            },
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if response.status_code == 200:
            data = response.json()
            self.config["subscription_tier"] = tier
            self.config["subscription_status"] = data.get("status", "active")
            self._save_config()
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json().get("detail", "Subscription failed")}

    async def cancel_subscription(self) -> Dict[str, Any]:
        """Cancel current subscription."""
        tokens = self.get_stored_tokens()
        if not tokens:
            return {"success": False, "error": "Not authenticated"}

        response = await self.client.post(
            f"{self.api_base_url}/subscription/cancel",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if response.status_code == 200:
            self.config["subscription_status"] = "cancelling"
            self._save_config()
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json().get("detail", "Cancellation failed")}

    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        tokens = self.get_stored_tokens()
        if not tokens:
            return {
                "subscription_tier": "free",
                "monthly_usage": 0,
                "monthly_limit": 10,
                "subscription_status": "inactive"
            }

        response = await self.client.get(
            f"{self.api_base_url}/user/usage",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if response.status_code == 200:
            data = response.json()
            self.config["usage"] = {
                "monthly_usage": data.get("monthly_usage", 0),
                "monthly_limit": data.get("monthly_limit", 10),
                "reset_date": data.get("usage_reset_date")
            }
            self.config["subscription_tier"] = data.get("subscription_tier", "free")
            self.config["subscription_status"] = data.get("subscription_status", "inactive")
            self._save_config()
            return data
        else:
            return self.config.get("usage", {})

    async def ai_complete(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get AI completion from server.

        Args:
            prompt: The prompt to complete
            context: Optional context

        Returns:
            AI completion response
        """
        tokens = self.get_stored_tokens()
        if not tokens:
            return {"success": False, "error": "Not authenticated. Please login or use your own API key."}

        # Check local usage cache first
        usage = self.config.get("usage", {})
        if usage.get("monthly_usage", 0) >= usage.get("monthly_limit", 10):
            return {
                "success": False,
                "error": f"Monthly limit reached ({usage['monthly_limit']} requests). Upgrade your plan for more."
            }

        response = await self.client.post(
            f"{self.api_base_url}/ai/complete",
            json={
                "prompt": prompt,
                "context": context or {},
                "model": "gpt-3.5-turbo",
                "max_tokens": 500
            },
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if response.status_code == 200:
            data = response.json()
            # Update local usage cache
            self.config["usage"]["monthly_usage"] += 1
            self._save_config()
            return {"success": True, "data": data}
        elif response.status_code == 429:
            return {"success": False, "error": "Rate limit exceeded. Please try again later."}
        elif response.status_code == 401:
            # Try to refresh token
            await self.refresh_token()
            return {"success": False, "error": "Authentication expired. Please login again."}
        else:
            return {"success": False, "error": response.json().get("detail", "AI service error")}

    async def brilliant_budgie(self, project_info: Dict, request_type: str) -> Dict[str, Any]:
        """Get Brilliant Budgie idea from server.

        Args:
            project_info: Project information
            request_type: Type of idea (test, refactor, performance, docs, creative)

        Returns:
            Brilliant Budgie idea
        """
        tokens = self.get_stored_tokens()
        if not tokens:
            return {"success": False, "error": "Brilliant Budgies require authentication"}

        # Check if user has access
        if self.config.get("subscription_tier") == "free":
            return {
                "success": False,
                "error": "Brilliant Budgie ideas require a paid subscription. Upgrade to Friendly tier or higher!"
            }

        response = await self.client.post(
            f"{self.api_base_url}/ai/brilliant-budgie",
            json={
                "project_info": project_info,
                "request_type": request_type
            },
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if response.status_code == 200:
            data = response.json()
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json().get("detail", "Budgie service error")}

    async def refresh_token(self) -> bool:
        """Refresh authentication token."""
        tokens = self.get_stored_tokens()
        if not tokens or "refresh_token" not in tokens:
            return False

        response = await self.client.post(
            f"{self.api_base_url}/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )

        if response.status_code == 200:
            data = response.json()
            self.store_tokens(data["access_token"], tokens["refresh_token"])
            return True
        return False

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        tokens = self.get_stored_tokens()
        return tokens is not None and "access_token" in tokens

    def get_subscription_info(self) -> Dict[str, Any]:
        """Get current subscription information."""
        return {
            "user": self.config.get("user"),
            "tier": self.config.get("subscription_tier", "free"),
            "status": self.config.get("subscription_status", "inactive"),
            "usage": self.config.get("usage", {}),
            "authenticated": self.is_authenticated()
        }

    def should_use_local_api(self) -> bool:
        """Check if local API key should be used."""
        # Check if user has local OpenAI API key
        import os
        has_local_key = bool(os.getenv("OPENAI_API_KEY"))

        # Use local key if available and user is not subscribed
        if has_local_key and self.config.get("subscription_tier") == "free":
            return True

        # Always use server if subscribed
        if self.config.get("subscription_tier") != "free":
            return False

        return has_local_key

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()