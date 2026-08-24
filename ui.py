import shutil
import sys


# ANSI color codes
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    BLACK   = "\033[30m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_DARK  = "\033[48;5;235m"


def _width():
    return min(shutil.get_terminal_size((80, 20)).columns, 90)


class UI:
    def banner(self):
        w = _width()
        print()
        print(f"{C.CYAN}{C.BOLD}{'─' * w}{C.RESET}")
        title = "  ⬡  D A R K W I R E  ⬡"
        sub   = "  Encrypted P2P · No logs · No trace"
        print(f"{C.CYAN}{C.BOLD}{title}{C.RESET}")
        print(f"{C.DIM}{sub}{C.RESET}")
        print(f"{C.CYAN}{'─' * w}{C.RESET}")
        print()

    def section(self, label: str):
        print(f"  {C.MAGENTA}{C.BOLD}◈  {label}{C.RESET}")
        print()

    def divider(self):
        w = _width()
        print(f"{C.DIM}{'─' * w}{C.RESET}")

    def info(self, msg: str):
        print(f"  {C.BLUE}ℹ{C.RESET}  {msg}")

    def success(self, msg: str):
        print(f"  {C.GREEN}✔{C.RESET}  {C.GREEN}{msg}{C.RESET}")

    def error(self, msg: str):
        print(f"\n  {C.RED}✘{C.RESET}  {C.RED}{msg}{C.RESET}\n")

    def hint(self, msg: str):
        print(f"  {C.DIM}{msg}{C.RESET}")

    def ask(self, label: str, default: str = "") -> str:
        if default:
            prompt = f"  {C.YELLOW}?{C.RESET}  {label} [{C.DIM}{default}{C.RESET}]: "
        else:
            prompt = f"  {C.YELLOW}?{C.RESET}  {label}: "
        val = input(prompt).strip()
        return val if val else default

    def input_prompt(self, name: str) -> str:
        """Input line that won't visually clash with incoming messages."""
        try:
            prompt = f"{C.CYAN}{C.BOLD}[{name}]{C.RESET} "
            return input(prompt).strip()
        except EOFError:
            return ""

    def print_incoming(self, name: str, msg: str, ts: str):
        """Print a received message, clearing the current input line first."""
        # Move to start of line, clear it, print message, then reprint prompt stub
        sys.stdout.write(f"\r\033[2K")
        line = (
            f"  {C.DIM}{ts}{C.RESET}  "
            f"{C.GREEN}{C.BOLD}{name}{C.RESET}"
            f"{C.DIM} ›{C.RESET} "
            f"{msg}"
        )
        print(line)

    def print_outgoing(self, name: str, msg: str, ts: str):
        """Echo the sent message above the prompt (already typed, just style it)."""
        # Move up one line, clear, reprint styled
        sys.stdout.write(f"\033[1A\r\033[2K")
        line = (
            f"  {C.DIM}{ts}{C.RESET}  "
            f"{C.CYAN}{C.BOLD}{name}{C.RESET}"
            f"{C.DIM} ›{C.RESET} "
            f"{msg}"
        )
        print(line)

    def print_file_sent(self, name: str, file_name: str, ts: str):
        sys.stdout.write(f"\033[1A\r\033[2K")
        line = (
            f"  {C.DIM}{ts}{C.RESET}  "
            f"{C.CYAN}{C.BOLD}{name}{C.RESET}"
            f"{C.DIM} ›{C.RESET} "
            f"{C.YELLOW}📎 sent file:{C.RESET} {file_name}"
        )
        print(line)

    def print_file_recv(self, name: str, file_name: str, ts: str):
        sys.stdout.write(f"\r\033[2K")
        line = (
            f"  {C.DIM}{ts}{C.RESET}  "
            f"{C.GREEN}{C.BOLD}{name}{C.RESET}"
            f"{C.DIM} ›{C.RESET} "
            f"{C.YELLOW}📎 file saved:{C.RESET} {file_name}"
        )
        print(line)
