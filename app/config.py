import os
import json
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Firebase
    firebase_service_account_json: Optional[str] = None
    firebase_credentials_path: Optional[str] = "app/music-type.json"
    firebase_database_url: str = "https://your-project-default-rtdb.firebaseio.com/"
    firebase_project_id: str = "sample-music-65323"
    firebase_storage_bucket: str = "sample-music-65323.firebasestorage.app"

    # Saavn API
    saavn_api_base_url: str = "https://www.jiosaavn.com/api.php"

    # Server
    app_env: str = "development"
    allowed_origins: str = "*"

    @property
    def firebase_credentials(self) -> Optional[dict]:
        """Load Firebase credentials from file (dev) or env JSON string (prod)."""
        if self.firebase_credentials_path and os.path.exists(self.firebase_credentials_path):
            try:
                with open(self.firebase_credentials_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not read Firebase credentials file: {e}")

        if self.firebase_service_account_json:
            try:
                return json.loads(self.firebase_service_account_json)
            except json.JSONDecodeError as e:
                print(f"⚠️  Invalid Firebase JSON: {e}")
                return None

        return None

    @property
    def origins_list(self) -> list:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Startup log
if settings.firebase_credentials:
    print("✅ Firebase credentials loaded")
else:
    print("⚠️  Firebase credentials not found — auth will not work")
    print("   Set FIREBASE_CREDENTIALS_PATH (local) or FIREBASE_SERVICE_ACCOUNT_JSON (prod)")
