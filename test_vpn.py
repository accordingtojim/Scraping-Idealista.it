#name file = test_vpn.py
import os
import random
import subprocess
import time

# Detect correct OpenVPN path (Intel or ARM)
OPENVPN_PATH = "/opt/homebrew/sbin/openvpn" if os.path.exists("/opt/homebrew/sbin/openvpn") else "/usr/local/sbin/openvpn"

# ProtonVPN DNS Servers
PROTONVPN_DNS = ["10.8.8.1", "10.8.8.2"]

def set_vpn_dns():
    """
    Automatically sets ProtonVPN DNS servers (10.8.8.1 & 10.8.8.2) on macOS.
    """
    try:
        subprocess.run(["networksetup", "-setdnsservers", "Wi-Fi"] + PROTONVPN_DNS, check=True)
        print("✅ ProtonVPN DNS applied successfully!")

        # Verify DNS settings
        result = subprocess.run(["networksetup", "-getdnsservers", "Wi-Fi"], capture_output=True, text=True)
        print("🔍 Current DNS servers:", result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting DNS: {e}")

def reset_dns():
    """
    Resets DNS settings to automatic (removes custom DNS).
    """
    try:
        subprocess.run(["networksetup", "-setdnsservers", "Wi-Fi", "Empty"], check=True)
        print("🔄 DNS settings reset to automatic.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error resetting DNS: {e}")

def connect_vpn():
    """
    Connects to a random ProtonVPN server using OpenVPN on macOS.
    """
    vpn_folder = os.path.expanduser("./VPN_config/")
    vpn_files = [f for f in os.listdir(vpn_folder) if f.endswith(".ovpn")]

    if not vpn_files:
        print("❌ No VPN config files found!")
        return

    selected_vpn = random.choice(vpn_files)
    full_vpn_path = os.path.join(vpn_folder, selected_vpn)

    print(f"🌍 Connecting to: {selected_vpn}")
    
    # Run OpenVPN and log errors
    result = os.system(f"sudo {OPENVPN_PATH} --config {full_vpn_path} --daemon")
    time.sleep(5)
    
    if result != 0:
        print("⚠️ Error: OpenVPN did not start properly. Check if the config file is correct.")
        return

    # Apply ProtonVPN DNS after connecting
    set_vpn_dns()

def disconnect_vpn():
    """
    Disconnects the currently running OpenVPN connection and reset DNS.
    """
    os.system("sudo pkill openvpn")
    print("🔌 VPN disconnected.")

    # Reset DNS to automatic
    reset_dns()

def check_vpn_status():
    """
    Checks the current IP address to verify VPN connection.
    """
    try:
        time.sleep(2)
        ip = subprocess.check_output("curl -s ifconfig.me", shell=True).decode().strip()
        print(f"🌍 Current Public IP: {ip}")
        return ip
    except Exception as e:
        print(f"❌ Error checking IP: {e}")
        return None


#chflags -R nouchg *.ovpn
#xattr -dr com.apple.quarantine *.ovpn
disconnect_vpn()
reset_dns()

