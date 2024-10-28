rule masepie_campaign_htmlstarter
{
    meta:
        description = "Detect Malicious Web page HTML file from CERT-UA#8399"
        references = "TRR240101;https://cert.gov.ua/article/6276894"
        hash = "628bc9f4aa71a015ec415d5d7d8cb168359886a231e17ecac2e5664760ee8eba"
        date = "2024-01-24"
        author = "HarfangLab"
        context = "file"
    strings:
        $s1 = "<link rel=\"stylesheet\" href=\"a.css\">" ascii wide fullword
        $s2 = "src=\".\\Capture" ascii wide
    condition:
        filesize > 600 and filesize < 5KB
        and (all of them)
}

rule masepie_campaign_webdavlnk
{
    meta:
        description = "Detect Malicious LNK from CERT-UA#8399"
        references = "TRR240101;https://cert.gov.ua/article/6276894"
        hash = "19d0c55ac466e4188c4370e204808ca0bc02bba480ec641da8190cb8aee92bdc"
        date = "2024-01-24"
        author = "HarfangLab"
        context = "file"
    strings:
        $a1 = "[system.Diagnostics.Process]::Start('msedge','http" wide nocase fullword
        $a2 = "\\Microsoft\\Edge\\Application\\msedge.exe" wide nocase fullword
        $a3 = "powershell.exe" ascii wide fullword
        $s1 = "win-j5ggokh35ap" ascii fullword
        $s2 = "desktop-q0f4sik" ascii fullword
    condition:
        filesize > 1200 and filesize < 5KB
        and (uint16be(0) == 0x4c00)
        and (
            (all of ($a*))
            or (any of ($s*))
        )
}

rule masepie_campaign_masepie
{
    meta:
        description = "Detect MASEPIE from CERT-UA#8399"
        references = "TRR240101;https://cert.gov.ua/article/6276894"
        hash = "18f891a3737bb53cd1ab451e2140654a376a43b2d75f6695f3133d47a41952b6"
        date = "2024-01-24"
        author = "HarfangLab"
        context = "file"
    strings:
        $t1 = "Try it againg" ascii wide fullword
        $t2 = "{user}{SEPARATOR}{k}" ascii wide fullword
        $t3 = "Error transporting file" ascii wide fullword
        $t4 = "check-ok" ascii wide fullword
        $a1 = ".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))" ascii wide fullword
        $a2 = "dec_file_mes(mes, key)" ascii wide fullword
        $a3 = "os.popen('whoami').read()" ascii wide fullword
    condition:
        filesize > 2KB and filesize < 15MB
        and (4 of them)
}

rule masepie_campaign_oceanmap
{
    meta:
        description = "Detect OCEANMAP from CERT-UA#8399"
        references = "TRR240101;https://cert.gov.ua/article/6276894"
        hash = "24fd571600dcc00bf2bb8577c7e4fd67275f7d19d852b909395bebcbb1274e04"
        date = "2024-01-24"
        modified = "2024-01-31"
        author = "HarfangLab"
        context = "file"
    strings:
        $dotNet = ".NETFramework,Version" ascii fullword
        $a1 = "$ SELECT INBOX.Drafts" wide fullword
        $a2 = "$ SELECT Drafts" wide fullword
        $a3 = "$ UID SEARCH subject \"" wide fullword
        $a4 = "$ APPEND INBOX {" wide fullword
        $a5 = "+FLAGS (\\Deleted)" wide fullword
        $a6 = "$ EXPUNGE" wide fullword
        $a7 = "BODY.PEEK[text]" wide fullword
        $t1 = "change_time" ascii fullword
        $t2 = "ReplaceBytes" ascii fullword
        $t3 = "fcreds" ascii fullword
        $t4 = "screds" ascii fullword
        $t5 = "r_creds" ascii fullword
        $t6 = "comp_id" ascii fullword
        $t7 = "changesecond" wide fullword
        $t8 = "taskkill /F /PID" wide fullword
        $t9 = "cmd.exe" wide fullword
    condition: 
        filesize > 8KB and filesize < 100KB
        and (uint16be(0) == 0x4D5A)
        and $dotNet
        and (3 of ($a*))
        and (2 of ($t*))
}