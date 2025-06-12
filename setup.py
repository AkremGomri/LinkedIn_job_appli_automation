#!/usr/bin/env python3
"""
Setup script for LinkedIn Job Application Automation
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has credentials"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and fill in your LinkedIn credentials")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'LINKEDIN_EMAIL=' in content and 'LINKEDIN_PASSWORD=' in content:
            # Check if they're not empty
            lines = content.strip().split('\n')
            email_set = any(line.startswith('LINKEDIN_EMAIL=') and '=' in line and line.split('=', 1)[1].strip() for line in lines)
            password_set = any(line.startswith('LINKEDIN_PASSWORD=') and '=' in line and line.split('=', 1)[1].strip() for line in lines)
            
            if email_set and password_set:
                print("✅ Environment variables configured!")
                return True
            else:
                print("⚠️  Please fill in your LinkedIn credentials in the .env file")
                return False
    return False

def main():
    print("🚀 Setting up LinkedIn Job Application Automation...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check environment setup
    if not check_env_file():
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your LinkedIn email and password in .env")
        print("3. Run: python main.py")
        return
    
    print("\n🎉 Setup complete!")
    print("\n🏃 To start the automation:")
    print("python main.py")
    
    print("\n⚠️  Important notes:")
    print("- Make sure you have Chrome browser installed")
    print("- The script will pause for 2FA/captcha - complete it manually")
    print("- Review the job search settings in config/settings.py")

if __name__ == "__main__":
    main()