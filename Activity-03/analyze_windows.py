# Adding new imports for subprocess and platform-specific checks
import platform
import argparse
import subprocess  

# Existing script content omitted for brevity...
# Append below the original `win_services` function

# ══════════════════════════════════════════════════════════════════════════
# Task 3: Windows Services Auditor (win-services)
# ══════════════════════════════════════════════════════════════════════════

def win_services(watch_list, fix):
    print("\n🛡️  Windows Services Audit")
    try:
        output = subprocess.check_output(["sc", "query", "type=", "service", "state=", "all"], text=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to query services – try running as Administrator.")
        return

    services = []
    service = {}
    for line in output.splitlines():
        if not line.strip():
            if service:
                services.append(service)
            service = {}
        else:
            if ":" in line:
                key, val = line.split(":", 1)
                service[key.strip()] = val.strip()

    # Filter for watched services if provided
    if watch_list:
        filtered = [svc for svc in services if svc.get("SERVICE_NAME", "").lower() in [w.lower() for w in watch_list]]
    else:
        filtered = services

    stopped = [svc for svc in filtered if svc.get("STATE", "").startswith("STOPPED")]

    if stopped:
        print("Stopped services:")
        for svc in stopped:
            print(f"  {svc.get('SERVICE_NAME', '?')}")
        if fix:
            for svc in stopped:
                name = svc.get('SERVICE_NAME', '')
                try:
                    subprocess.check_call(["sc", "start", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"  ▶️  Attempted to start {name}")
                except Exception:
                    print(f"  ❌ Failed to start {name}")
    else:
        print("All watched services are running.")

# ══════════════════════════════════════════════════════════════════════════
# Task 4: Scheduled-Task auditor (win-tasks)
# ══════════════════════════════════════════════════════════════════════════

def win_tasks():
    print("\n📆 Scheduled Task Audit (non-Microsoft)")
    try:
        output = subprocess.check_output(["schtasks", "/Query", "/FO", "LIST", "/V"], text=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to query scheduled tasks – try running as Administrator.")
        return

    tasks = []
    task = {}
    for line in output.splitlines():
        if not line.strip():
            if task and "Microsoft" not in task.get("TaskName", ""):
                tasks.append((task.get("TaskName", "?"), task.get("Next Run Time", "?")))
            task = {}
        else:
            if ":" in line:
                key, val = line.split(":", 1)
                task[key.strip()] = val.strip()

    if tasks:
        width = max(len(name) for name, _ in tasks)
        print(f"{'Task Name':<{width}} {'Next Run Time'}")
        print("-" * (width + 20))
        for name, next_time in tasks:
            print(f"{name:<{width}} {next_time}")
    else:
        print("No non-Microsoft scheduled tasks found.")

# ══════════════════════════════════════════════════════════════════════════
# Task 5: Shadow-Copy space check (win-vss)
# ══════════════════════════════════════════════════════════════════════════

def win_vss():
    print("\n💾 Shadow Copy Space Check")
    try:
        output = subprocess.check_output(["vssadmin", "list", "shadowstorage"], text=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to list shadow storage – run as Administrator.")
        return

    current, max_size = None, None
    for line in output.splitlines():
        if "Used Shadow Copy Storage space" in line:
            current = line.split(":", 1)[1].strip()
        elif "Maximum Shadow Copy Storage space" in line:
            max_size = line.split(":", 1)[1].strip()

    print("Used Storage:", current or "N/A")
    print("Max Storage:", max_size or "N/A")

    # Optional: Warn if used exceeds 10% of max (simplistic check using GB/TB only)
    try:
        def parse_size(s):
            s = s.upper()
            if "GB" in s:
                return float(s.split(" ")[0]) * 1
            elif "TB" in s:
                return float(s.split(" ")[0]) * 1024
            return 0

        used = parse_size(current)
        maximum = parse_size(max_size)
        if maximum and used / maximum > 0.10:
            print("⚠️  Warning: Shadow copy storage exceeds 10% of maximum size")
    except Exception:
        print("(Could not calculate usage percentage)")

# Update CLI parser to recognize the new tasks
# Modify the `main()` function:

def main():
    p = argparse.ArgumentParser(description="Windows admin toolkit (IT 390R)")
    p.add_argument("--task", required=True,
                   choices=["win-events", "win-pkgs", "win-services", "win-tasks", "win-vss"],
                   help="Which analysis to run")

    p.add_argument("--hours", type=int, default=24,
                   help="Look-back window for Security log (win-events)")
    p.add_argument("--min-count", type=int, default=1,
                   help="Min occurrences before reporting (win-events)")
    p.add_argument("--csv", metavar="FILE", default=None,
                   help="Export installed-software list to CSV (win-pkgs)")
    p.add_argument("--watch", nargs="*", metavar="SVC", default=[],
                   help="Service names to check (win-services)")
    p.add_argument("--fix", action="store_true",
                   help="Attempt to start stopped services (win-services)")

    args = p.parse_args()

    if args.task == "win-events":
        win_events(args.hours, args.min_count)
    elif args.task == "win-pkgs":
        win_pkgs(args.csv)
    elif args.task == "win-services":
        win_services(args.watch, args.fix)
    elif args.task == "win-tasks":
        win_tasks()
    elif args.task == "win-vss":
        win_vss()
    
    # Dummy implementation for win_events to avoid NameError
    def win_events(hours, min_count):
        print("win_events function is not yet implemented.")

    # Dummy implementation for win_pkgs to avoid NameError
    def win_pkgs(csv_file):
        print("win_pkgs function is not yet implemented.")

if __name__ == "__main__":
    main()
# This script is designed to be run on Windows systems and requires administrative privileges for some tasks.
# Ensure you have the necessary permissions and environment to execute these commands.  