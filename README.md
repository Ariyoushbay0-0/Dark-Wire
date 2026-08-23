# DarkWire 🔌

![GitHub License](https://img.shields.io/badge/license-GPL-red)
![Python](https://img.shields.io/badge/python-3.10+-black)
![Status](https://img.shields.io/badge/status-active-darkgreen)

> No servers. No logs. No trace. Just two ends of a wire.

DarkWire is a peer-to-peer encrypted chat and file transfer tool built from scratch in Python. No central servers, no third parties, no one in between — just two endpoints communicating directly, with everything encrypted end-to-end.

Built for people who believe privacy is a right, not a privilege. Built for conditions where the wire is the only thing you can trust.

---

![banner](assets/banner.png)

---

## What It Does

- **P2P Architecture** — No central server. One peer hosts, one peer connects. Direct line.
- **End-to-End Encryption** — RSA-3072 for key exchange. AES-256 for everything else.
- **Encrypted File Transfer** — Any file. Any size. Fully encrypted over the wire.
- **No Logs. No Memory.** — Keys live in RAM and die when the session ends. Nothing touches disk.
- **Named Sessions** — Both peers identify themselves by name. You know who you're talking to.
- **Works Anywhere** — No infrastructure needed. As long as there's a connection, DarkWire works.

---

## How It Works

```
Peer A (host)                      Peer B (client)
───────────────────────────────────────────────────
Generate RSA-3072 keypair          Generate RSA-3072 keypair
Send public key         ────────►
                        ◄────────  Send public key
Generate AES-256 key
Encrypt AES key with B's RSA
Send encrypted AES key  ────────►
                                   Decrypt AES key with own RSA

          ── All communication is now AES-256 encrypted ──

[Aria]: hey             ════════►
                        ◄════════  [Alex]: hey
/file document.pdf      ════════►  [FILE RECEIVED: document.pdf]
```

---

## Installation

```bash
git clone https://github.com/Ariyoushbay0-0/darkwire.git
cd darkwire

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

**Host a session:**
```bash
python3 main.py
# Choose: 1
# Enter port: 9999
# Enter your name: Aria
# Waiting for connection...
```

**Join a session:**
```bash
python3 main.py
# Choose: 2
# Enter IP: 192.168.1.x
# Enter port: 9999
# Enter your name: Alex
```

**Send a file:**
```
[Aria]: /file /path/to/file.pdf
```

---

## Encryption

| Layer | Algorithm | Purpose |
|-------|-----------|---------|
| Key Exchange | RSA-3072 | Securely deliver the AES session key |
| Short Messages | RSA-3072 | Messages under 290 bytes |
| Long Messages | AES-256-CBC | Messages over 290 bytes |
| File Transfer | AES-256-CBC | All file data |

Session keys are generated fresh every time. Nothing is reused. Nothing is stored.

---

## Project Structure

```
darkwire/
├── main.py       # Entry point
├── server.py     # Host logic
├── client.py     # Client logic
├── crypto.py     # Encryption engine (RSA + AES)
└── requirements.txt
```

---

## Screenshots

![chat](assets/chat.png)
![file](assets/file.png)

---

## License

DarkWire is licensed under the **GNU General Public License v3.0**.

Any derivative work must remain open source under the same license.
See [LICENSE](LICENSE) for details.

---

*Two endpoints. One wire. Zero eyes.*

— [@Ariyoushbay0-0](https://github.com/Ariyoushbay0-0)
