# Benchmark Answers (Ground Truth)

Use these to compare against the chatbot's output. Don't just read the chatbot's
answer and judge "does this sound right?" -- actually place the two side by side
and check each of the three sections individually.

These are written based on standard industry definitions (NIST, OWASP, and
common security fundamentals). If you're ever unsure about one yourself,
cross-check it against your ADCD notes or a second independent source before
trusting either version.

---

### Firewall
- **What:** A system (hardware or software) that monitors and controls incoming/outgoing network traffic based on defined security rules.
- **Why:** To block unauthorized access while allowing legitimate traffic through, acting as a barrier between trusted and untrusted networks.
- **Where:** Network perimeters, individual devices (host-based firewalls), cloud environments (security groups).
- **Expected keywords:** packet filtering, inbound/outbound traffic, rules, network perimeter, trusted vs. untrusted

### VPN (Virtual Private Network)
- **What:** Creates an encrypted tunnel over a public network (like the internet) to securely connect a user to a private network.
- **Why:** Protects data confidentiality in transit and enables secure remote access to internal resources.
- **Where:** Remote work access, securing traffic on public Wi-Fi.
- **Expected keywords:** encrypted tunnel, remote access, encapsulation, confidentiality

### DNS (Domain Name System)
- **What:** Translates human-readable domain names (like google.com) into IP addresses computers use to find each other.
- **Why:** Humans remember names more easily than numbers; DNS automates that translation.
- **Where:** Every time you browse the internet; also used internally in corporate networks.
- **Expected keywords:** domain name resolution, IP address, DNS query, DNS record

### Phishing
- **What:** A social engineering attack where attackers impersonate a trusted entity to trick victims into revealing sensitive information or installing malware.
- **Why:** To steal credentials, financial data, or gain initial network access.
- **Where:** Email (most common), SMS (smishing), phone calls (vishing), fake websites.
- **Expected keywords:** social engineering, spoofed sender, credential harvesting, malicious link/attachment

### Encryption
- **What:** Converts readable data (plaintext) into an unreadable format (ciphertext) using an algorithm and a key.
- **Why:** Protects data confidentiality so only authorized parties with the correct key can read it.
- **Where:** Securing data in transit (HTTPS, VPN) and data at rest (encrypted disks/databases).
- **Expected keywords:** plaintext, ciphertext, encryption key, confidentiality

### Multi-Factor Authentication (MFA)
- **What:** Requires two or more independent proofs of identity before granting access (something you know, have, or are).
- **Why:** Reduces risk of unauthorized access even if one factor (like a password) is compromised.
- **Where:** Logging into email, banking apps, corporate VPNs, cloud services.
- **Expected keywords:** something you know/have/are, one-time password (OTP), authentication factor

### Zero-Day Vulnerability
- **What:** A security flaw unknown to the software vendor, with no official patch available yet.
- **Why:** Attackers can exploit it before defenders get a chance to fix it -- especially dangerous.
- **Where:** Found in operating systems, browsers, applications; often used in targeted/advanced attacks.
- **Expected keywords:** unpatched vulnerability, exploit, patch, vendor disclosure

### SIEM (Security Information and Event Management)
- **What:** A platform that collects, aggregates, and analyzes log data from across an organization's systems to detect security events.
- **Why:** Centralizes visibility into security events, enabling faster detection and investigation.
- **Where:** Used by SOC analysts for monitoring and incident investigation (e.g., Splunk, Microsoft Sentinel).
- **Expected keywords:** log aggregation, correlation rules, centralized visibility, alerting

### Incident Response
- **What:** The structured process an organization follows to detect, contain, eradicate, and recover from a security incident.
- **Why:** Minimizes damage, reduces recovery time/cost, prevents recurrence.
- **Where:** Used by SOC/CSIRT teams responding to malware infections, breaches, unauthorized access.
- **Expected keywords:** containment, eradication, recovery, root cause analysis

### Threat Intelligence
- **What:** Information about current or emerging threats (attacker tactics, indicators of compromise) used to inform security decisions.
- **Why:** Enables proactive defense against adversary behavior, rather than purely reactive responses.
- **Where:** SOC threat hunting, enriching SIEM alerts, informing detection rules.
- **Expected keywords:** indicators of compromise (IOCs), threat actor, TTPs, MITRE ATT&CK

### False Positive
- **What:** An alert indicating malicious activity when the activity was actually legitimate/benign.
- **Why:** Too many false positives cause alert fatigue and waste analyst time.
- **Where:** Common in SIEM/IDS alerting; addressed through detection rule tuning.
- **Expected keywords:** alert fatigue, detection tuning, benign activity

### Zero Trust
- **What:** A security model that assumes no user or device should be automatically trusted, even inside the network perimeter.
- **Why:** Traditional perimeter-based security fails once an attacker gets inside; zero trust limits lateral movement and damage.
- **Where:** Implemented via strict identity verification, micro-segmentation, least privilege access.
- **Expected keywords:** least privilege, continuous verification, micro-segmentation, lateral movement
