"""
Paystack Payment Integration Service
"""
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# Paystack Configuration
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_4159f5e5ad916f0f2cf2aca7d3449a85325d865a")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_fc1e890e6a2376e2b25029cac638eaf1fc099c2f")
PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackService:
    """Service for handling Paystack payment operations"""
    
    def __init__(self):
        self.secret_key = PAYSTACK_SECRET_KEY
        self.public_key = PAYSTACK_PUBLIC_KEY
        self.base_url = PAYSTACK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def initialize_transaction(
        self,
        email: str,
        amount_kobo: int,
        reference: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a Paystack transaction
        
        Args:
            email: Customer email
            amount_kobo: Amount in kobo (smallest currency unit)
            reference: Unique transaction reference (auto-generated if not provided)
            callback_url: URL to redirect after payment
            metadata: Additional data to attach to transaction
        
        Returns:
            Dict containing authorization_url, reference, and access_code
        """
        if reference is None:
            reference = f"STF_{uuid.uuid4().hex[:12].upper()}"
        
        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
            "metadata": metadata or {}
        }
        
        if callback_url:
            payload["callback_url"] = callback_url
        
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "access_code": data["data"]["access_code"],
                    "reference": data["data"]["reference"]
                }
            else:
                return {
                    "success": False,
                    "message": data.get("message", "Failed to initialize transaction")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
    
    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """
        Verify a Paystack transaction
        
        Args:
            reference: Transaction reference
        
        Returns:
            Dict containing verification result and transaction details
        """
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                transaction_data = data["data"]
                return {
                    "success": True,
                    "status": transaction_data.get("status"),  # success, failed, abandoned
                    "reference": transaction_data.get("reference"),
                    "amount": transaction_data.get("amount"),
                    "paid_at": transaction_data.get("paid_at"),
                    "channel": transaction_data.get("channel"),
                    "gateway_response": transaction_data.get("gateway_response"),
                    "metadata": transaction_data.get("metadata"),
                    "customer": transaction_data.get("customer"),
                    "authorization": transaction_data.get("authorization")
                }
            else:
                return {
                    "success": False,
                    "message": data.get("message", "Failed to verify transaction")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
    
    def verify_webhook_signature(self, signature: str, request_body: bytes) -> bool:
        """
        Verify Paystack webhook signature
        
        Args:
            signature: X-Paystack-Signature header value
            request_body: Raw request body bytes
        
        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.secret_key.encode(),
            request_body,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def parse_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Paystack webhook event
        
        Args:
            event_data: Webhook payload
        
        Returns:
            Parsed event information
        """
        event_type = event_data.get("event", "")
        data = event_data.get("data", {})
        
        return {
            "event": event_type,
            "reference": data.get("reference"),
            "status": data.get("status"),
            "amount": data.get("amount"),
            "paid_at": data.get("paid_at"),
            "channel": data.get("channel"),
            "customer_email": data.get("customer", {}).get("email"),
            "metadata": data.get("metadata", {})
        }


# Singleton instance
paystack_service = PaystackService()
