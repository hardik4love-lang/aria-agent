# CEH v12 & OSCP+ Accelerated Mentorship & Lab Roadmap
**Prepared by ARIA Cyber Security Operations**

## 1. Core Methodology Mapping
- **Reconnaissance & Enumeration**: Nmap automated NSE scripting, Gobuster / Feroxbuster directory fuzzing, autorecon pipelines.
- **Vulnerability Assessment**: Manual analysis of web services, banner grabbing, CVE exploitation verification.
- **Weaponization & Initial Access**: Reverse shell handlers, bypass restricted shells, payload generation (msfvenom & custom C/Python payloads).
- **Privilege Escalation (Linux)**:
  - SUID binaries (`find / -perm -u=s -type f 2>/dev/null`)
  - Sudo privileges (`sudo -l`) & GTFOBins
  - Cronjob hijacking, PATH injection, and Kernel exploits.
- **Privilege Escalation (Windows)**:
  - Unquoted service paths, AlwaysInstallElevated registry keys
  - Token impersonation (PrintSpoofer, GodPotato)
  - Active Directory enumeration with BloodHound & PowerView.

## 2. Weekly Hands-On Milestones
- **Week 1-2**: CEH Theory & Networking fundamentals, Wireshark packet dissection, nmap scripting.
- **Week 3-4**: Proving Grounds & HackTheBox Easy/Medium Linux machines (focus on manual enumeration without automated scanners).
- **Week 5-6**: Windows Buffer Overflow / AD attacking vectors, Kerberoasting, AS-REP roasting.
- **Week 7-8**: Mock 24-hour OSCP exam lab simulation and report writing template.
