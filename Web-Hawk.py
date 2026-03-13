import nmap
import socket
import os
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from tqdm import tqdm

# --- INITIALIZATION ---
console = Console()

# --- CONFIGURATION ---
# IMPORTANT: Do not hardcode your real webhook here if uploading to GitHub!
DISCORD_WEBHOOK = "" 

# --- COLORS ---
G, C, R, Y, W, B, NC = '[bold green]', '[bold cyan]', '[bold red]', '[bold yellow]', '[white]', '[bold blue]', '[/]'

def clean_target(raw_input):
    """Cleans the input to get a pure domain or IP."""
    target = raw_input.replace("https://", "").replace("http://", "").split('/')[0].strip()
    return target

def send_webhook(msg):
    """Sends findings to Discord via Webhook."""
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=5)
        except Exception:
            pass

def print_banner():
    """Displays the Predator Recon Engine Banner with Legal Disclaimer."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = f"""{C}
  ██╗    ██╗███████╗██████╗ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗
  ██║    ██║██╔════╝██╔══██╗██║  ██║██╔══██╗██║    ██║██║ ██╔╝
  ██║ █╗ ██║█████╗  ██████╔╝███████║███████║██║ █╗ ██║█████╔╝
  ██║███╗██║██╔══╝  ██╔══██╗██╔══██║██╔══██║██║███╗██║██╔═██╗
  ╚███╔███╔╝███████╗██████╔╝██║  ██║██║  ██║╚███╔███╔╝██║  ██╗
   ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝
{W}               {R}🦅 THE PREDATOR RECON ENGINE v1.0 🦅{W}
{C}  ──────────────────────────────────────────────────────────────────────────{NC}"""
    console.print(banner)
    
    # --- LEGAL DISCLAIMER IN BANNER ---
    disclaimer = f"{R}[!] FOR EDUCATIONAL PURPOSES ONLY. THE DEVELOPER IS NOT RESPONSIBLE FOR ANY ILLEGAL USE.{NC}"
    console.print(Panel(disclaimer, border_style="red", expand=False))
    
    console.print(f"  {Y}STATUS:{G} HUNTING {W}| {Y}OPERATOR:{R} SADFRIENDS {W}| {Y}TYPE:{B} AGGRESSIVE{NC}\n")

def start_framework():
    print_banner()
    prompt = f"{B}┌──({G}WebHawk@Shell{B})─[{W}~{B}]\n└─{G}$ {W}Target Domain: "
    raw_target = console.input(prompt).strip()
    
    if not raw_target:
        console.print(f"{R}[!] No target entered.{NC}")
        return
        
    target = clean_target(raw_target)

    try:
        ip = socket.gethostbyname(target)
        console.print(f"\n{B}[{W}i{B}]{W} Hawk Eye Locked On: {G}{target} {W}({Y}{ip}{W})")
    except socket.gaierror:
        console.print(f"{R}[!] Error: Target domain resolution failed.{NC}")
        return

    nm = nmap.PortScanner()
    
    # Scanning phases
    steps = [
        {"desc": "Spotting Services", "args": "-Pn -sV -T4 --top-ports 100"},
        {"desc": "Diving for Flaws", "args": "-Pn -sV --script vuln,exploit,http-sql-injection,http-xssed,http-csrf --script-timeout 150s"}
    ]

    for step in tqdm(steps, desc=f"{B}WebHawk Hunting{NC}", bar_format="{l_bar}{bar:20}{r_bar}", colour="cyan"):
        try:
            nm.scan(ip, arguments=step["args"])
        except Exception as e:
            console.print(f"{R}[!] Scan error: {e}{NC}")
            continue

    # 1. INTEL DASHBOARD TABLE
    res_table = Table(box=None, header_style="bold magenta")
    res_table.add_column("PORT", style="cyan", justify="center")
    res_table.add_column("SERVICE/VERSION", style="white")
    res_table.add_column("RISK LEVEL", justify="center")

    vuln_list = []
    
    if not nm.all_hosts():
        console.print(f"{R}[!] No hosts found or host is down.{NC}")
        return

    for h in nm.all_hosts():
        for p in nm[h].all_protocols():
            ports = sorted(nm[h][p].keys())
            for port in ports:
                d = nm[h][p][port]
                is_v = 'script' in d
                risk = f"{R}● CRITICAL{NC}" if is_v else f"{G}○ SECURE{NC}"
                
                res_table.add_row(
                    str(port), 
                    f"{d['name']} {d.get('version', '')}", 
                    risk
                )
                
                if is_v:
                    for s_id, s_res in d['script'].items():
                        vuln_list.append(f"Port {port}: {s_id}")

    console.print("\n", Panel(res_table, title=f"{B} WEBHAWK INTEL ", border_style="blue", expand=False))

    # 2. VULNERABILITIES & WEBHOOK LOGIC
    if vuln_list:
        v_table = Table(box=None, header_style="bold red")
        v_table.add_column("🦅 PREY SPOTTED (VULNERABILITIES)", style="bold red")

        unique_list = sorted(list(set(vuln_list)))
        webhook_msg = f"🦅 **WebHawk v1.0 Notification**\nTarget: `{target}`\nPrey Found:\n"

        for v in unique_list:
            v_table.add_row(v)
            webhook_msg += f"- {v}\n"

        console.print(Panel(v_table, title=f"{R} CRITICAL FLAWS ", border_style="red"))
        send_webhook(webhook_msg)

        # EXPERT GUIDE / NEXT STEPS
        guide = f"{Y}[SQLi]{W} Potential injection found! Use sqlmap for deep testing.\n{Y}[XSS]{W} Manual check recommended for reflection points."
        console.print(Panel(guide, title=f"{G} NEXT STEPS FOR OPERATOR ", border_style="green"))
    else:
        console.print(Panel(f"{G}The target is clean. No prey found for WebHawk.{NC}", border_style="green"))

    console.print(f"\n{B}[{W}√{B}]{W} Hunt Finished. WebHawk is resting...{NC}\n")

if __name__ == "__main__":
    try:
        start_framework()
    except KeyboardInterrupt:
        console.print(f"\n{R}[!] Operation aborted. We are out of here!{NC}")
    except Exception as e:
        console.print(f"\n{R}[!] Unexpected error: {e}{NC}")
    finally:
        # Final Legal Reminder on Exit
        console.print(f"{Y}[Notice] Remember: This tool is for educational purposes and authorized testing only.{NC}")
