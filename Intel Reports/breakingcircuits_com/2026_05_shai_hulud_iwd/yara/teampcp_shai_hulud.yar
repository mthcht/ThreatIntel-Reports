// Source: https://github.com/breakingcircuits1337/Shai-Hulud-Carnage-APT-Report
// Author: breakingcircuit / Breaking Circuits LLC
// Date: 2026-05-13
// TLP: WHITE
// Description: Detection rules for Shai-Hulud / TeamPCP / Carnage APT supply chain worm

import "pe"

rule TeamPCP_GhTokenMonitor_Script {
    meta:
        description = "Detects the gh-token-monitor persistence script dropped by Shai-Hulud malware"
        author = "breakingcircuit"
        date = "2026-05-13"
        reference = "https://github.com/breakingcircuits1337/Shai-Hulud-Carnage-APT-Report"
        severity = "CRITICAL"
    strings:
        $s1 = "gh-token-monitor" ascii
        $s2 = "com.user.gh-token-monitor" ascii
        $s3 = "STARTED_FILE" ascii
        $s4 = "MAX_TTL=86400" ascii
        $s5 = "CHECK_INTERVAL=60" ascii
        $s6 = "api.github.com/user" ascii
        $s7 = "Bearer ${GITHUB_TOKEN}" ascii
        $s8 = "40[0-9]" ascii
    condition:
        4 of them
}

rule TeamPCP_DeadmanSwitch_Installer {
    meta:
        description = "Detects the deadman switch installer — sets rm -rf handler on token revocation"
        author = "breakingcircuit"
        date = "2026-05-13"
        reference = "https://github.com/breakingcircuits1337/Shai-Hulud-Carnage-APT-Report"
        severity = "CRITICAL"
    strings:
        $s1 = "GH_TOKEN" ascii
        $s2 = "HANDLER" ascii
        $s3 = "gh-token-monitor" ascii
        $s4 = "LaunchAgents" ascii
        $s5 = "systemd/user" ascii
        $s6 = "loginctl enable-linger" ascii
        $s7 = "SuccessfulExit" ascii
        $s8 = "bootstrap" ascii nocase
        $s9 = "bootout" ascii nocase
        $handler = "rm -rf" ascii
    condition:
        $handler and 5 of ($s*)
}

rule TeamPCP_NpmPublish_MaliciousUA {
    meta:
        description = "Detects Shai-Hulud hardcoded NPM publish User-Agent"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $ua  = "npm/11.13.1 node/v24.10.0" ascii
        $reg = "registry.npmjs.org" ascii
        $pub = "Npm-Command" ascii
        $auth = "Npm-Auth-Type" ascii
    condition:
        $ua and ($reg or $pub or $auth)
}

rule TeamPCP_BunLoader_BashVariant {
    meta:
        description = "Detects BASH_LOADER dropper bootstrapping Bun runtime"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "bun-linux-x64-musl-baseline" ascii
        $s2 = "bun-linux-aarch64" ascii
        $s3 = "bun-darwin-aarch64" ascii
        $s4 = "oven-sh/bun/releases/download" ascii
        $s5 = "ENTRY_SCRIPT" ascii
        $s6 = "ai_init.js" ascii
        $s7 = "resolve_asset" ascii
    condition:
        4 of them
}

rule TeamPCP_BunLoader_PythonVariant {
    meta:
        description = "Detects PYTHON_LOADER dropper bootstrapping Bun runtime"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "router_runtime.js" ascii
        $s2 = "bun-linux-x64-musl-baseline" ascii
        $s3 = "oven-sh/bun/releases/download" ascii
        $s4 = "BUN_INSTALL_DIR" ascii
        $s5 = "resolve_asset_name" ascii
        $s6 = "get_musl_status" ascii
    condition:
        4 of them
}

rule TeamPCP_NodeLoader_ConfigMjs {
    meta:
        description = "Detects config.mjs node-based Bun dropper"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "bun-linux-x64-musl-baseline" ascii
        $s2 = "bun-darwin-aarch64" ascii
        $s3 = "oven-sh/bun/releases" ascii
        $s4 = "ai_init.js" ascii
        $s5 = "is_alpine_or_musl" ascii wide
        $s6 = "0x04034b50" ascii
        $s7 = "0x02014b50" ascii
    condition:
        4 of them
}

rule TeamPCP_PythonUtil_MemDump {
    meta:
        description = "Detects python_util.py — reads Runner.Worker process memory to extract CI/CD secrets"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "CRITICAL"
    strings:
        $s1 = "Runner.Worker" ascii
        $s2 = "/proc/" ascii
        $s3 = "/maps" ascii
        $s4 = "/mem" ascii
        $s5 = "sys.stdout.buffer.write" ascii
        $s6 = "cmdline" ascii
    condition:
        5 of them
}

rule TeamPCP_GitHubActions_SecretsExfil_Workflow {
    meta:
        description = "Detects malicious workflow.yml exfiltrating GitHub Actions secrets"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "CRITICAL"
    strings:
        $s1 = "VARIABLE_STORE" ascii
        $s2 = "toJSON(secrets)" ascii
        $s3 = "format-results.txt" ascii
        $s4 = "format-results" ascii
        $s5 = "upload-artifact" ascii
        $s6 = "de0fac2e4500dabe0009e67214ff5f5447ce83dd" ascii
    condition:
        $s2 and 3 of them
}

rule TeamPCP_VSCode_TasksPersistence {
    meta:
        description = "Detects malicious VSCode tasks.json running setup on folder open"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "runOn" ascii
        $s2 = "folderOpen" ascii
        $s3 = "setup.mjs" ascii
        $s4 = "Environment Setup" ascii
    condition:
        all of them
}

rule TeamPCP_ClaudeSettings_Hook {
    meta:
        description = "Detects malicious .claude/settings.json hooking Claude Code SessionStart"
        author = "breakingcircuit"
        date = "2026-05-13"
        reference = "Distinct from ~/.claude.json token scraping — this is a SessionStart execution hook"
        severity = "HIGH"
    strings:
        $s1 = "SessionStart" ascii
        $s2 = "setup.mjs" ascii
        $s3 = "hooks" ascii
        $s4 = ".vscode" ascii
        $s5 = ".claude" ascii
    condition:
        $s1 and $s2 and $s3 and ($s4 or $s5)
}

rule TeamPCP_GitHubExfil_ResultsNaming {
    meta:
        description = "Detects exfiltration result file naming pattern in attacker GitHub repos"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "MEDIUM"
    strings:
        $pattern  = /results-[0-9]{13}-[0-9]+\.json(\.p[0-9]+)?/
        $dir      = "results/" ascii
        $key      = "\"key\":" ascii
        $envelope = "\"envelope\":" ascii
    condition:
        $pattern and $envelope and $key
}

rule TeamPCP_Sigstore_FakeProvenance {
    meta:
        description = "Detects attempt to forge Sigstore provenance bundles for poisoned NPM packages"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "fulcio.sigstore.dev" ascii
        $s2 = "rekor.sigstore.dev" ascii
        $s3 = "application/vnd.dev.sigstore.bundle.v0.3+json" ascii
        $s4 = "proofOfPossession" ascii
        $s5 = "proposedContent" ascii
        $s6 = "generateProvenanceBundle" ascii
    condition:
        4 of them
}

rule TeamPCP_C2_Domain_Reference {
    meta:
        description = "Detects reference to known C2 domain git-tanstack.com"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "CRITICAL"
    strings:
        $domain = "git-tanstack.com" ascii wide
    condition:
        $domain
}

rule TeamPCP_OpenSearch_TargetPackage {
    meta:
        description = "Detects targeting of opensearch-project/opensearch-js for supply chain attack"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "@opensearch-project/opensearch" ascii
        $s2 = "opensearch-js" ascii
        $s3 = "release-drafter.yml" ascii
        $s4 = "OIDC" ascii
        $s5 = "npm/v1/oidc/token/exchange" ascii
    condition:
        ($s1 or $s2) and ($s3 or $s5)
}

rule TeamPCP_LockFile_IOC {
    meta:
        description = "Detects Shai-Hulud lock file preventing double-execution"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "MEDIUM"
    strings:
        $lockfile = "tmp.ts018051808.lock" ascii
    condition:
        $lockfile
}

rule TeamPCP_SearchString_CommitMarker {
    meta:
        description = "Detects beacon strings and commit markers used by TeamPCP"
        author = "breakingcircuit"
        date = "2026-05-13"
        severity = "HIGH"
    strings:
        $s1 = "IfYouRevokeThisTokenItWillWipeTheComputerOfTheOwner" ascii
        $s2 = "thebeautifulmarchoftime" ascii
        $s3 = "thebeautifulsnadsoftime" ascii
    condition:
        any of them
}
