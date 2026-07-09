#!/usr/bin/env python3
import os
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define Google Calendar API access scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.json')
    creds_path = os.path.join(script_dir, 'credentials.json')
    
    creds = None
    
    # Load existing token.json if present
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print("🔑 Found existing token.json file.")
        except Exception as e:
            print(f"⚠️ Failed to parse existing token: {e}. Re-authenticating.")
            creds = None
            
    # Authenticate if credentials are not valid/validity has expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("⏳ Access token expired. Refreshing with Google...")
            try:
                creds.refresh(Request())
                print("🔄 Token refreshed successfully!")
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}. Initializing full login flow.")
                creds = None
                
        # Run OAuth flow if refresh failed or no credentials found
        if not creds:
            if not os.path.exists(creds_path):
                print("\n❌ Error: credentials.json not found!")
                print("=" * 60)
                print("Please follow the setup instructions to create OAuth credentials in Google Cloud:")
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("2. Enable the Google Calendar API.")
                print("3. Configure the OAuth Consent Screen (set user type to External, add your email).")
                print("4. Go to Credentials -> Create Credentials -> OAuth Client ID (Desktop App).")
                print(f"5. Download the client secrets JSON file, save it here as:\n   {creds_path}")
                print("=" * 60)
                sys.exit(1)
                
            print("🌐 Starting local authentication server...")
            print("👉 A browser window should open. Log in with your Google Account to authorize Scribe.")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                # Run the server on a free local port
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"❌ OAuth Flow Failed: {e}")
                sys.exit(1)
                
        # Write token.json
        try:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            print(f"✅ Credentials successfully saved to: {token_path}")
        except Exception as e:
            print(f"❌ Failed to save token: {e}")
            sys.exit(1)
            
    print("\n🎉 Scribe is authenticated and ready to manage your calendar!")

if __name__ == '__main__':
    main()
