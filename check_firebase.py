import sys
import os
from app.config import settings

def check_config():
    print("🔍 Checking Firebase Backend Configuration...")
    print(f"   Project ID:      {settings.firebase_project_id}")
    print(f"   Database URL:    {settings.firebase_database_url}")
    print(f"   Storage Bucket:  {settings.firebase_storage_bucket}")
    print(f"   Creds Path:      {settings.firebase_credentials_path}")
    
    # Check if credentials file exists
    if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
        print("✅ Credentials file found.")
    else:
        print("❌ Credentials file NOT found at the specified path.")
        print("   ⚠️  Authentication and Database writes will fail.")
        print("   👉 Action: Download 'service-account-file.json' from Firebase Console -> Project Settings -> Service Accounts")
        print("   👉 Action: Rename it to 'firebase-credentials.json' and place it in 'backend/app/'")
        
    print("\n✅ Configuration loaded into settings.")

if __name__ == "__main__":
    check_config()
