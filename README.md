# MyEduConnect: Ethical Hacking & Penetration Testing 🛡️

**Course:** CCS6324 - Ethical Hacking & Penetration
**Project Focus:** Web Application Security, OS Exploitation, and Systems Hardening

## Overview
This repository contains the source code, evidence files, and documentation for the **MyEduConnect** learning portal. The project demonstrates a full penetration testing lifecycle: building a deliberately vulnerable environment, conducting reconnaissance, exploiting web and OS-level vulnerabilities, and finally engineering robust security patches and network defenses.

## Technology Stack
* **Backend:** Python 3, Flask, Werkzeug
* **Database:** SQLite
* **Frontend:** HTML, CSS
* **Security & Infrastructure:** TLS/HTTPS, UFW (Firewall), Snort (IDS), ModSecurity (WAF), Kali Linux 

## Project Phases & Vulnerabilities Addressed

### Phase 1: Vulnerable Environment Setup
Built a custom LMS platform and a secondary REST API containing intentional OWASP Top 10 vulnerabilities and misconfigurations.
* Insecure authentication & hardcoded cryptography keys.
* Vulnerable OS permissions and open anonymous FTP.

### Phase 2 & 3: Reconnaissance & Sniffing
* **Tools used:** Nmap, Dirb, Nikto, curl, Wireshark.
* Mapped the network, enumerated HTTP methods, brute-forced hidden directories, and intercepted cleartext FTP credentials and unencrypted session cookies.

### Phase 4: Exploitation (The Attack)
Successfully weaponized the environment to achieve complete system compromise:
1. **SQL Injection (SQLi):** Bypassed the login portal.
2. **Stored XSS:** Injected malicious JavaScript into the admin dashboard.
3. **Broken Object Level Authorization (BOLA/IDOR):** Accessed restricted payment and REST API endpoints.
4. **Anonymous FTP:** Exfiltrated the backend SQLite database (`database.db`).
5. **Privilege Escalation:** Exploited a misconfigured SUID bit on `/bin/bash` to gain `root` access and extract `/etc/shadow`.

### Phase 5: Defense & Hardening (The Patch)
Refactored the codebase and locked down the operating system to prevent all Phase 4 exploits:
* **Code Remediation:** Implemented parameterized queries, HTML entity escaping, and strict token/session validation.
* **Cryptography:** Generated secure session entropy, hashed passwords using PBKDF2:sha256, and deployed TLS certificates to force HTTPS.
* **OS & Network Hardening:** Disabled anonymous FTP, stripped SUID bits, configured UFW to block unauthorized ports, and deployed Snort (IDS) and ModSecurity (WAF) to detect and block malicious payloads.

---

## 🚀 Clean Redeployment Guide

**Prerequisites:**
* An Ubuntu/Linux environment.
* Python 3 and `pip` installed.
* Ensure ports 5000 and 5001 are available.

**Step 1: Extract and Setup the Environment**
Clone this repository and set up the Python virtual environment:
```bash
git clone [https://github.com/Jinyuan0415/CCS6324-ETHICAL-HACKING-PENETRATION.git](https://github.com/Jinyuan0415/CCS6324-ETHICAL-HACKING-PENETRATION.git)
cd CCS6324-ETHICAL-HACKING-PENETRATION/MyEduConnect
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install flask werkzeug
