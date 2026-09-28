import os
import sys
import threading
from dotenv import load_dotenv
from app import create_app

load_dotenv()

def start_flask(app, port):
    # Disable debug reloader in thread to prevent duplicate tunnels
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    port = int(os.environ.get('PORT', 5000))
    authtoken = os.environ.get('NGROK_AUTHTOKEN', '').strip()

    print("=" * 65)
    print("[*] FinAura AI Advisor - Ngrok Public Deployment Launcher")
    print("=" * 65)

    try:
        from pyngrok import ngrok, conf

        if authtoken:
            print("[+] Configuring Ngrok authtoken from .env...")
            ngrok.set_auth_token(authtoken)
        else:
            print("[!] NOTICE: No NGROK_AUTHTOKEN found in .env.")
            print("    Get a free token from https://dashboard.ngrok.com/get-started/your-authtoken")
            print("    Attempting to connect with default/existing tunnel config...\n")

        # Open public tunnel
        public_tunnel = ngrok.connect(port, proto="http")
        public_url = public_tunnel.public_url

        print("\n" + "*" * 65)
        print(f"[+] PUBLIC LIVE DEMO URL: {public_url}")
        print(f"[+] LOCAL URL:            http://127.0.0.1:{port}")
        print("*" * 65 + "\n")
        print("Share the PUBLIC LIVE DEMO URL above with any browser or mobile device!\n")

    except Exception as e:
        print(f"\n[-] Ngrok Tunnel Initialization Notice: {e}")
        print("[i] Falling back to standard local host execution.\n")
        public_url = f"http://127.0.0.1:{port}"

    app = create_app('development')
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
