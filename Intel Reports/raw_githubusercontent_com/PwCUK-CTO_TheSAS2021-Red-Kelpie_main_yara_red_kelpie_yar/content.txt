/*
Copyright 2021 PwC UK

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

rule Motnug_Loader_API_Loading_Structure : Red_Kelpie {

	meta:
		description = "Detects Motnug loader samples based off dynamic API loading into a unique structure"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		license = "Apache License, Version 2.0"
		copyright = "Copyright PwC UK 2021 (C)"
		created_date = "2021-05-18"
		modified_date = "2021-05-18"
		revision = "0"
		hash = "fde7363bcdde850585774177655b15a24344212d3ebe2e14026ffeb024b34010"
		hash = "64bcbaf174e0027c2ec1f4d18ccffd8f4b856286bcbf8d4a416cad4a30726d90"
		hash = "fcbd7ab82939b7e0aff38f48a1797ac2efdb3c01c326a2dcf828a500015e0e83"
		reference = "https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/higaisa-or-winnti-apt-41-backdoors-old-and-new/"

	strings:
		/*
		Example routine being signatured below
		mov  ecx, cs:dword_180018914
		call  dyn_load_api
		mov  rcx, rax
		mov  rax, cs:qword_180019E70
		mov  [rax+48h], rcx		     <- the +48h is a unique offset into the structure
		*/
		
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 08}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 10}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 18}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 20}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 28}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 30}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 38}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 40}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 48}
		$ = {8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B C8 48 8B 05 ?? ?? ?? ?? 48 89 48 50}

	condition:
		uint16(0) == 0x5A4D and filesize < 2MB and 5 of them
}

rule APT41_ChaChaLoader : Red_Kelpie {

	meta:
		description = "Detects ChaChaLoader, which has been observed loading Cobalt Strike, and has been loaded by loaded by Motnug"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-05-18"
		modified_date = "2021-05-18"
		revision = "0"
		hash = "d9d269a199ca0841fc71fef045c3dc5701a5042bea46d05a657b6db43fe55acc"

	strings:
		// EtwEventWrite + system
		$str_block = {45 74 77 45 76 65 6E 74 57 72 69 74 65 00 00 00 73 79 73 74 65 6D 00}
		
		$mutex1 = "Global\\kREwdFrOlvASgP4zWZyV89m6T2K0bIno"
		$mutex2 = "Global\\v5EPQFOImpTLaGZes3Nl1JSKHku8AyCw"
		$mutex3 = "Global\\Dw0EluZTRM3Kye4Hv65IGfoaX9sSP7VA"

		
	condition:
		uint16(0) == 0x5A4D and any of them
}

rule APT41_Batch_Script_CobaltStrike_Loader : Red_Kelpie {

	meta:
		description = "Detects unique strings from a .bat script used by APT41 to load Cobalt Strike"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-05-21"
		modified_date = "2021-05-21"
		revision = "0"
		reference = "https://www.fireeye.com/blog/threat-research/2020/03/apt41-initiates-global-intrusion-campaign-using-multiple-exploits.html"
		hash = "62d9e8f6e8ade53c6756f66beaaf4b9d93da6d390bf6f3ae1340389178a2fa29"
		hash = "49e338c5ae9489556ae8f120a74960f3383381c91b8f03061ee588f6ad97e74c"
		hash = "2fb5766af3d68c210e62518263b2f29ca4c50100c99b6979c3d0e19f05af6a39"

	strings:
		$set1 = "set \"WORK_DIR="
		$set2 = "set \"DLL_NAME="
		$set3 = "set \"SERVICE_NAME="
		$set4 = "set \"DISPLAY_NAME="
		$set5 = "set \"DESCRIPTION="
		
		$sc1 = "sc stop %SERVICE_NAME%"
		$sc2 = "sc delete %SERVICE_NAME%"
		$sc3 = "sc create \"%SERVICE_NAME%\" binPath= \"%SystemRoot%\\system32\\svchost.exe -k %SERVICE_NAME%\" type= share start= auto error= ignore DisplayName= \"%DISPLAY_NAME%\""
		$sc4 = "SC failure \"%SERVICE_NAME%\" reset= 86400 actions= restart/60000/restart/60000/restart/60000"
		$sc5 = "sc description \"%SERVICE_NAME%\" \"%DESCRIPTION%\""
		
		
		$reg1 = "reg add \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Svchost\" /v \"%SERVICE_NAME%\" /t REG_MULTI_SZ /d \"%SERVICE_NAME%\" /f"
		$reg2 = "reg add \"HKLM\\SYSTEM\\CurrentControlSet\\Services\\%SERVICE_NAME%\\Parameters\" /f"
		$reg3 = "reg add \"HKLM\\SYSTEM\\CurrentControlSet\\Services\\%SERVICE_NAME%\\Parameters\" /v \"ServiceDll\" /t REG_EXPAND_SZ /d \"%WORK_DIR%\\%DLL_NAME%\" /f"

		$other1 = "dp0%DLL_NAME%\" \"%WORK_DIR%\" /Y"
		$other2 = "net start \"%SERVICE_NAME%\""
		
	condition:
		4 of ($set*) or 4 of ($sc*) or 2 of ($reg*) or all of ($other*)
}

rule APT41_Custom_ChaCha20_Routine_32bit : Red_Kelpie {

	meta:
		description = "Detects 32-bit samples that use a custom ChaCha20 algorithm, observed in various APT41 samples (including Motnug and a second stage Cobalt Strike loader). This version is observed using a 256-bit key, and a 96-bit nonce, and manually sets the block counter to 19."
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-05-24"
		modified_date = "2021-05-24"
		revision = "0"
		hash = "c5fb7442b0c04a18495f4c4168f88abbe9101996d0c47c9fbfffcdd1e4bb7a54"
		reference = "https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/higaisa-or-winnti-apt-41-backdoors-old-and-new/"

	strings:
		$mov_word_via_shifts = {0F B6 4A 01 0F B6 02 8D 52 04 C1 E1 08 0B C8 0F B6 42 FB C1 E1 08 0B C8 0F B6 42 FA C1 E1 08 0B C8 89 0F 8D 7F 04 83 EB 01 75 D5}
		$xor_routine = {8D 0C 30 8A 04 0A 32 04 37 46 88 01 8B 85 78 FF FF FF 3B F3}
		
	condition:
		all of them
}

rule APT41_Custom_ChaCha20_Routine_64bit : Red_Kelpie {

	meta:
		description = "Detects 64-bit samples that use a custom ChaCha20 algorithm, observed in various APT41 samples (including Motnug and a second stage Cobalt Strike loader). This version is observed using a 256-bit key, and a 96-bit nonce, and manually sets the block counter to 19."
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-05-24"
		modified_date = "2021-05-24"
		revision = "0"
		hash = "64bcbaf174e0027c2ec1f4d18ccffd8f4b856286bcbf8d4a416cad4a30726d90"
		hash = "98f6be546c5191b67014e3d0f7f8df86715d970aa326a6a438d0be234daf8841"
		hash = "afb5e3f05d2eedf6e0e7447a34ce6fd135a72dad11660cf21bec4178d0edc15b"
		reference = "https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/higaisa-or-winnti-apt-41-backdoors-old-and-new/"

	strings:
		$mov_word_via_shifts = {0F B6 02 0F B6 4A 01 C1 E1 08 0B C8 0F B6 42 FF C1 E1 08 0B C8 0F B6 42 FE C1 E1 08 0B C8 41 89 0C 10 48 8D 52 04 49 83 E9 01 75 D4}
		$xor_routine = {8A 04 0F 32 01 41 88 04 08 48 FF C1 48 8D 04 0A 48 3B C6}
		
	condition:
		all of them
}

rule APT41_AES128_CryptDeriveKey_Routine : Red_Kelpie
{
	meta:
		description = "Detects custom routine used alongside the Windows APIs to derive an AES-128 key used by APT41 in Motnug samples"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-06-15"
		modified_date = "2021-06-15"
		revision = "0"
		hash = "b39e498bf51f0622eca174a127d4c1e83e8c4bc2beab696a423788ed621d1911"
		hash = "fde7363bcdde850585774177655b15a24344212d3ebe2e14026ffeb024b34010"
		hash = "48dc6ba89c34c59408b1bbb67de715adf17611a696b579a8f58e833081ccc9fe"

	strings:
		// mov byte ptr [rcx+20h], 0
		// lea rdi, [rcx+28h]
		// and qword ptr [rdi], 0
		// lea r14, [rcx+30h]
		// and qword ptr [r14], 0
		// lea rsi, [rcx+38h]
		// and qword ptr [rsi], 0
		$ = {C6 41 20 00 48 8D 79 28 48 83 27 00 4C 8D 71 30 49 83 26 00 48 8D 71 38 48 83 26 00}
		
	condition:
		uint16(0) == 0x5A4D and all of them
}

rule APT41_Time_Bound_Guardrail : Red_Kelpie
{
	meta:
		description = "Detects a check against the system's year to see if it is greater than 2021, which is used as a guardrail/failsafe in APT41 samples like Motnug"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-06-16"
		modified_date = "2021-06-16"
		revision = "0"
		hash = "45d175f3c1cb6067f60ea90661524124102f872830a78968f46187d6bc28f70d"
		hash = "5347c5bbfaec8877c3b909ff80cda82f505c3ef6384a9ecf040c821fc7829736"
		hash = "bfe2673b02c54be9093cff8fd564b630109175c608f07d94e4a2ac65028a6eae"

	strings:
		// 0FB7442430      MOVZX EAX,WORD PTR [RSP+30]
		// B9E3070000      MOV ECX,000007E3 <- this converts to 2019 in Base10
		// 662BC1          SUB AX,CX
		// 6683F802        CMP AX,0002 <- check if the value is greater than 2 difference from 2019
		// 77              JA
		$ = {0F B7 44 24 30 B9 E3 07 00 00 66 2B C1 66 83 F8 02 77}
		
	condition:
		uint16(0) == 0x5A4D and any of them
}

rule APT41_StealthMutant_GUID : Red_Kelpie
{
	meta:
		description = "Detects GUID from a .NET loader called StealthMutant used by APT41 to load Cobalt Strike/SideWalk"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-08-26"
		modified_date = "2021-08-26"
		revision = "0"
		hash = "04f6fc49da69838f5b511d8f996dc409a53249099bd71b3c897b98ad97fd867c"
		hash = "f10927293393f72935f9d25b629ae3e6adeba352f898f127edbb1a9ddcdb071c"
		hash = "a941fe06352fb12793c51226a84b418652354d5239832a4d9649e72bb8a9629b"
		hash = "0b40007ccb6e83cdb3c890c9af10ee45e91ee5d136f63232373dc25dfb7ddd99"
		hash = "b7b2aa801dea2ec2797f8cf43b99c4bf8d0c1effe532c0c800b40336e9012af2"
		reference = "https://www.welivesecurity.com/2021/08/24/sidewalk-may-be-as-dangerous-as-crosswalk/"
		reference = "https://documents.trendmicro.com/assets/white_papers/wp-earth-baku-an-apt-group-targeting-indo-pacific-countries.pdf"

	strings:
		$guid1 = "2506b21e-7317-8231-d506-f7114404c7dd" ascii wide nocase
		$guid2 = "40a952fc-952b-4793-8133-13c4a861aadc" ascii wide nocase
		$guid3 = "40a922fc-956b-4763-8233-11c2a851aadc" ascii wide nocase
		
	condition:
		any of them
}

rule APT41_StealthMutant_Strings : Red_Kelpie
{
	meta:
		description = "Detects strings from a .NET loader called StealthMutant used by APT41 to load Cobalt Strike/SideWalk"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-08-26"
		modified_date = "2021-08-26"
		revision = "0"
		hash = "b876c47131a12a845c7d6e47c0a6bf5006556f4b8bb861d798649cd052b79af1"
		hash = "34f95e0307959a376df28bc648190f72bccc5b25e0e00e45777730d26abb5316"
		hash = "24ac3cc305576493beefab026d1cb7cce84f3bfcbcc51cdb5e612c290499390a"
		hash = "b7b2aa801dea2ec2797f8cf43b99c4bf8d0c1effe532c0c800b40336e9012af2"
		hash = "890186ee89df998bbbf5b39ee31e946280dee1ac288f5489bb1d3af3b2f88f24"
		reference = "https://www.welivesecurity.com/2021/08/24/sidewalk-may-be-as-dangerous-as-crosswalk/"
		reference = "https://documents.trendmicro.com/assets/white_papers/wp-earth-baku-an-apt-group-targeting-indo-pacific-countries.pdf"

	strings:
		$unique1 = "ETWPatcher" ascii wide
		$unique2 = "UPrivate.Transmutation" ascii wide
		$unique3 = "UPrivate.DInvoke" ascii wide
		$unique4 = "WriteShellcodeToSection" ascii wide
		$unique5 = "BuildEntryPatchCode" ascii wide
		$unique6 = "GetEntryPointFromImage" ascii wide
		$unique7 = "MapAndPatchTargetProcess" ascii wide
		$unique8 = "DecodeFromPayloadFile" ascii wide
		$unique9 = "PuppetProcessPath" ascii wide

		$generic1 = "Hollower" ascii wide
		$generic2 = "USCInstaller" ascii wide
		$generic3 = "MagicString" ascii wide
		$generic4 = "PayloadProtocol" ascii wide
		$generic5 = "RunShellcode" ascii wide
		$generic6 = "workDirectory_" ascii wide
		$generic7 = "FindEntryPoint" ascii wide
		$generic8 = "LdrGetProcedureAddress" ascii wide
		$generic9 = "EnableMicrosoftSign" ascii wide

		$api_mb1 = "mb_ntdll" ascii wide
		$api_mb2 = "mb_kernel32" ascii wide
		$api_mb3 = "mb_LdrLoadDll" ascii wide
		$api_mb4 = "mb_LdrGetProcedureAddress" ascii wide
		$api_mb5 = "mb_RtlInitUnicodeString" ascii wide
		$api_mb6 = "mb_RtlUnicodeStringToAnsiString" ascii wide
		$api_mb7 = "mb_RtlFreeAnsiString" ascii wide
		$api_mb8 = "mb_RtlZeroMemory" ascii wide
		$api_mb9 = "mb_NtQueryInformationProcess" ascii wide
		$api_mb10 = "mb_NtCreateSection" ascii wide
		$api_mb11 = "mb_NtMapViewOfSection" ascii wide
		$api_mb12 = "mb_NtUnmapViewOfSection" ascii wide
		$api_mb13 = "mb_EtwEventWrite" ascii wide
		$api_mb14 = "mb_CloseHandle" ascii wide
		$api_mb15 = "mb_VirtualProtect" ascii wide
		$api_mb16 = "mb_ReadProcessMemory" ascii wide
		$api_mb17 = "mb_WriteProcessMemory" ascii wide
		$api_mb18 = "mb_CreateProcessW" ascii wide
		$api_mb19 = "mb_InitializeProcThreadAttributeList" ascii wide
		$api_mb20 = "mb_UpdateProcThreadAttribute" ascii wide
		$api_mb21 = "mb_ResumeThread" ascii wide
		$api_mb22 = "mb_GetSystemInfo" ascii wide
		$api_mb23 = "mb_GetCurrentProcess" ascii wide
		$api_mb24 = "mb_ShellcodeFileName" ascii wide
		$api_mb25 = "mb_PuppetProcessPath" ascii wide
		
		$api_get1 = "get_ntdll" ascii wide
		$api_get2 = "get_kernel32" ascii wide
		$api_get3 = "get_LdrLoadDll" ascii wide
		$api_get4 = "get_LdrGetProcedureAddress" ascii wide
		$api_get5 = "get_RtlInitUnicodeString" ascii wide
		$api_get6 = "get_RtlUnicodeStringToAnsiString" ascii wide
		$api_get7 = "get_RtlFreeAnsiString" ascii wide
		$api_get8 = "get_RtlZeroMemory" ascii wide
		$api_get9 = "get_NtQueryInformationProcess" ascii wide
		$api_get10 = "get_NtCreateSection" ascii wide
		$api_get11 = "get_NtMapViewOfSection" ascii wide
		$api_get12 = "get_NtUnmapViewOfSection" ascii wide
		$api_get13 = "get_EtwEventWrite" ascii wide
		$api_get14 = "get_CloseHandle" ascii wide
		$api_get15 = "get_VirtualProtect" ascii wide
		$api_get16 = "get_ReadProcessMemory" ascii wide
		$api_get17 = "get_WriteProcessMemory" ascii wide
		$api_get18 = "get_CreateProcessW" ascii wide
		$api_get19 = "get_InitializeProcThreadAttributeList" ascii wide
		$api_get20 = "get_UpdateProcThreadAttribute" ascii wide
		$api_get21 = "get_ResumeThread" ascii wide
		$api_get22 = "get_GetSystemInfo" ascii wide
		$api_get23 = "get_GetCurrentProcess" ascii wide
		$api_get24 = "get_ShellcodeFileName" ascii wide
		$api_get25 = "get_PuppetProcessPath" ascii wide
		
	condition:
		any of ($unique*) or 5 of ($generic*) or (any of ($api_get*) and any of ($api_mb*))
}

rule APT41_Icon_Location_LNK : Red_Kelpie
{
	meta:
		description = "Detects LNK files masquerading as PDFs likely used by APT41"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-08-26"
		modified_date = "2021-08-26"
		revision = "0"
		hash = "2218904238dc4f8bb5bb838ed4fa779f7873814d7711a28ba59603826ae020aa"
		hash = "5904bc90aec64b12caa5d352199bd4ec2f5a3a9ac0a08adf954689a58eff3f2a"
		hash = "c98ac83685cb5f7f72e832998fec753910e77d1b8eee638acb508252912f6cf6"
		hash = "a44b35f376f6e493580c988cd697e8a2d64c82ab665dfd100115fb6f700bb82a"


	strings:
		$pdf = ".\\1.pdf" ascii wide
		$doc = ".\\1.doc" ascii wide

	condition:
		uint32be(0) == 0x4C000000 and
		uint32be(4) == 0x01140200 and
		uint32be(8) == 0x00000000 and
		uint32be(12) == 0xC0000000 and
		uint32be(16) == 0x00000046 and
		any of them
}

rule APT41_LNK_Machine_Identifier : Red_Kelpie
{
	meta:
		description = "Detects LNK files masquerading as PDFs with machine identifiers likely used by Red Kelpie"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-08-31"
		modified_date = "2021-08-31"
		revision = "0"
		hash = "2218904238dc4f8bb5bb838ed4fa779f7873814d7711a28ba59603826ae020aa"
		hash = "59fa89a19aa236aec216f0c8e8d59292b8d4e1b3c8b5f94038851cc5396d6513"
		hash = "5904bc90aec64b12caa5d352199bd4ec2f5a3a9ac0a08adf954689a58eff3f2a"
		hash = "2bd9f22f5e6cf13073e465b2f4d9ce0af74ff7dc408003eceee98545e70fe4e3"
		hash = "c98ac83685cb5f7f72e832998fec753910e77d1b8eee638acb508252912f6cf6"
		hash = "a44b35f376f6e493580c988cd697e8a2d64c82ab665dfd100115fb6f700bb82a"


	strings:
		$ = "desktop-nua5ghe" ascii wide
		$ = "desktop-dphthjm" ascii wide
		$ = "sharpe809" ascii wide
		$ = "work-pc" ascii wide
		$ = "desktop-d6ibtq1" ascii wide
		$ = "win-ii83b94l95i" ascii wide

	condition:
		uint32be(0) == 0x4C000000 and
		uint32be(4) == 0x01140200 and
		uint32be(8) == 0x00000000 and
		uint32be(12) == 0xC0000000 and
		uint32be(16) == 0x00000046 and
		any of them
}

rule APT41_SideWalk_Loader : Red_Kelpie
{
	meta:
		description = ".NET loader (which is packed with ConfuserEx) used to load SideWalk"
		TLP = "WHITE"
		author = "PwC Cyber Threat Operations :: BitsOfBinary"
		copyright = "Copyright PwC UK 2021 (C)"
		license = "Apache License, Version 2.0"
		created_date = "2021-09-09"
		modified_date = "2021-09-09"
		revision = "0"
		reference = "https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/grayfly-china-sidewalk-malware"
		hash = "1b5b37790b2029902d2d6db2da20da4d0d7846b20e32434f01b2d384eba0eded"
		hash = "b732bba813c06c1c92975b34eda400a84b5cc54a460eeca309dfecbe9b559bd4"

	strings:
		$ = "shellc0de"
		$ = "dotnet.4.x64"

	condition:
		uint16(0) == 0x5A4D and all of them
}
