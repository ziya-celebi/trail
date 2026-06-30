import subprocess
import shutil
import sys
import os

# --- 1. ATOMIC ACTIONS (The "Work") ---
def action_update_grub_standard():
    # Detects if it should use /boot/grub or /boot/grub2
    target = "/boot/grub/grub.cfg" if os.path.exists("/boot/grub/grub.cfg") else "/boot/grub2/grub.cfg"
    subprocess.run(["sudo", "grub-mkconfig", "-o", target], check=True)

def action_update_grub_fedora():
    # Fedora/RHEL standard path
    subprocess.run(["sudo", "grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"], check=True)

def action_update_initramfs_arch():
    subprocess.run(["sudo", "mkinitcpio", "-P"], check=True)

def action_update_initramfs_debian():
    subprocess.run(["sudo", "update-initramfs", "-u", "-k", "all"], check=True)

def action_update_initramfs_fedora():
    # Fedora/RHEL uses dracut
    subprocess.run(["sudo", "dracut", "-f"], check=True)

# --- 2. DETECTION LOGIC (The "Auto-Detect") ---
def get_available_tools():
    """Checks what system tools are available to build the menu dynamically."""
    detected = []

    # GRUB Detection
    if shutil.which("grub2-mkconfig"):
        detected.append(("Update GRUB (Fedora)", action_update_grub_fedora))
    elif shutil.which("grub-mkconfig"):
        detected.append(("Update GRUB", action_update_grub_standard))

    # Initramfs Detection
    if shutil.which("mkinitcpio"):
        detected.append(("Rebuild Initramfs (Arch)", action_update_initramfs_arch))
    elif shutil.which("update-initramfs"):
        detected.append(("Rebuild Initramfs (Debian)", action_update_initramfs_debian))
    elif shutil.which("dracut"):
        detected.append(("Rebuild Initramfs (Fedora)", action_update_initramfs_fedora))
        
    return detected

# --- 3. UI ENGINE ---
def execute_choice(tools, choice):
    if not choice.isdigit():
        return
    
    idx = int(choice) - 1
    if 0 <= idx < len(tools):
        try:
            print(f"[*] Running: {tools[idx][0]}...")
            tools[idx][1]() 
            print("[+] Action successful.")
        except subprocess.CalledProcessError as e:
            print(f"[-] Command failed: {e}")
    else:
        print("[-] Invalid selection.")

def run_interface():
    while True:
        tools = get_available_tools()
        print("\n=== Skrato Maintenance ===")
        for i, (name, _) in enumerate(tools, 1):
            print(f"[{i}] {name}")
        print("[q] Quit")
        
        user_input = input("\nSelect: ").strip().lower()
        if user_input == 'q':
            break
        execute_choice(tools, user_input)

if __name__ == "__main__":
    run_interface()
