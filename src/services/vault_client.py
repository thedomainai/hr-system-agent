"""
HashiCorp Vault client for secrets management.

Provides secure access to sensitive configuration and credentials.
"""

from typing import Any

import hvac

from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)


class VaultClient:
    """HashiCorp Vault client wrapper."""

    def __init__(self) -> None:
        self._client: hvac.Client | None = None
        self._mount_point: str = "secret"

    def connect(self) -> None:
        """Establish connection to Vault."""
        settings = get_settings()
        self._client = hvac.Client(
            url=settings.vault_addr,
            token=settings.vault_token,
        )
        if not self._client.is_authenticated():
            raise RuntimeError("Vault authentication failed")
        logger.info("vault_connected", url=settings.vault_addr)

    def disconnect(self) -> None:
        """Close Vault connection."""
        if self._client:
            self._client = None
            logger.info("vault_disconnected")

    @property
    def client(self) -> hvac.Client:
        """Get the Vault client instance."""
        if not self._client:
            raise RuntimeError("Vault client not connected")
        return self._client

    def read_secret(self, path: str) -> dict[str, Any] | None:
        """Read a secret from Vault KV v2."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self._mount_point,
            )
            return response["data"]["data"]
        except hvac.exceptions.InvalidPath:
            logger.warning("secret_not_found", path=path)
            return None
        except Exception as e:
            logger.error("vault_read_error", path=path, error=str(e))
            raise

    def write_secret(self, path: str, data: dict[str, Any]) -> None:
        """Write a secret to Vault KV v2."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point=self._mount_point,
            )
            logger.info("secret_written", path=path)
        except Exception as e:
            logger.error("vault_write_error", path=path, error=str(e))
            raise

    def delete_secret(self, path: str) -> None:
        """Delete a secret from Vault."""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self._mount_point,
            )
            logger.info("secret_deleted", path=path)
        except Exception as e:
            logger.error("vault_delete_error", path=path, error=str(e))
            raise

    # Application-specific secret access
    def get_gemini_api_key(self) -> str | None:
        """Get Gemini API key from Vault or settings."""
        secret = self.read_secret("hr-policy-advisor/gemini")
        if secret and "api_key" in secret:
            return secret["api_key"]
        # Fallback to environment variable
        settings = get_settings()
        return settings.gemini_api_key or None

    def get_database_credentials(self) -> dict[str, str] | None:
        """Get database credentials from Vault."""
        return self.read_secret("hr-policy-advisor/database")

    def get_company_secrets(self, company_id: str) -> dict[str, Any] | None:
        """Get company-specific secrets."""
        return self.read_secret(f"hr-policy-advisor/companies/{company_id}")

    def store_company_secrets(
        self, company_id: str, secrets: dict[str, Any]
    ) -> None:
        """Store company-specific secrets."""
        self.write_secret(f"hr-policy-advisor/companies/{company_id}", secrets)


# Singleton instance
_vault_client: VaultClient | None = None


def get_vault_client() -> VaultClient:
    """Get or create Vault client singleton."""
    global _vault_client
    if _vault_client is None:
        _vault_client = VaultClient()
        _vault_client.connect()
    return _vault_client


def close_vault_client() -> None:
    """Close Vault client if exists."""
    global _vault_client
    if _vault_client:
        _vault_client.disconnect()
        _vault_client = None
