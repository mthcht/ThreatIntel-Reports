# Shai-Hulud / Carnage APT — Incident Worm Disclosure (IWD)

Independent operational analysis of the Shai-Hulud GitHub worm campaign.
Published: 2026-05-13
Researcher: breakingcircuit / Breaking Circuits LLC (breakingcircuits.com)
Contact: security@breakingcircuits.com

## Source

https://github.com/breakingcircuits1337/Shai-Hulud-Carnage-APT-Report

## Included Artifacts

- content.txt   — narrative analysis and indicator context
- iocs.txt      — machine-parseable indicators, one per line, categorized
- timeline.txt  — chronological reconstruction of campaign and disclosure
- yara/         — YARA detection rules (16 rules, all dropper variants)
- screenshots/  — operational evidence preserved at disclosure time

## Campaign Summary

Supply chain worm targeting developer workstations and CI/CD runners.
Threat actor: TeamPCP / Carnage APT
Primary behaviors: NPM token theft, AWS credential harvesting (17 regions),
GitHub-based exfiltration, supply chain poisoning via forged Sigstore provenance,
host destruction on token revocation (deadman switch).

## Disclosure Context

No vendor remediation channel was available at time of disclosure.
Attacker-controlled infrastructure remained live during analysis.
Defensive artifacts (vaccine script, YARA rules, IOC set) were produced
and published while the threat was active.
HackerOne closed the deadman switch finding as "Informative."
