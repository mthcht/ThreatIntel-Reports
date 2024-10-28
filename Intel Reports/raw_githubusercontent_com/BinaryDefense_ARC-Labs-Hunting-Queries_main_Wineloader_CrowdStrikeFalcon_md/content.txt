**Detect certutil.exe with specific command line arguments:**

event_simpleName=ProcessRollup2 \| search (FileName="certutil.exe" AND CommandLine="\*certutil\*decode\*C:\\\\Windows\\\\Tasks\\\\\*")

**Detect file events in C:\\Windows\\Tasks\\ folder with specific file extensions:**

event_simpleName=FileRollup2 \| search (DirectoryPath="C:\\\\Windows\\\\Tasks\\\\" AND (FileName="\*.dll" OR FileName="\*.exe"))

**Detect schtasks.exe process with specific command line arguments:**

event_simpleName=ProcessRollup2 \| search (FileName="schtasks.exe" AND CommandLine="\*sqlwriter.exe\*")

**Detect registry events related to a specific registry key:**

event_simpleName=RegistryRollup2 \| search (RegistryKeyName="HKEY_CURRENT_USER\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\MS SQL Writer")

**Detect network events initiated by mshta process:**

event_simpleName=NetworkConnectRollup2 \| search (FileName="mshta")

**Detect file events initiated by mshta.exe:**

event_simpleName=FileRollup2 \| search (ParentBaseFileName="mshta.exe")

**Detect process events initiated by mshta.exe with specific command line arguments:**

event_simpleName=ProcessRollup2 \| search (ParentBaseFileName="mshta.exe" AND (CommandLine="\*tar\*-xf\*" OR CommandLine="\*unrar\*" OR CommandLine="\*7z\*e\*"))

**Detect image load events where sqlwriter.exe loaded vcruntime140.dll:**

event_simpleName=ImageLoadRollup2 \| search (ParentBaseFileName="sqlwriter.exe" AND FileName="vcruntime140.dll")

**Detect file events based on specific SHA256 hashes:**

event_simpleName=FileRollup2 \| search (SHA256 IN ("72b92683052e0c813890caf7b4f8bfd331a8b2afc324dd545d46138f677178c4", "ad43bbb21e2524a71bad5312a7b74af223090a8375f586d65ff239410bbd81a7", "3739b2eae11c8367b576869b68d502b97676fb68d18cc0045f661fbe354afcb9", "1c7593078f69f642b3442dc558cddff4347334ed7c96cd096367afd08dca67bc", "e477f52a5f67830d81cf417434991fe088bfec21984514a5ee22c1bcffe1f2bc", "f61cee951b7024fca048175ca0606bfd550437f5ba2824c50d10bef8fb54ca45", "c1223aa67a72e6c4a9a61bf3733b68bfbe08add41b73ad133a7c640ba265a19e", "b014cdff3ac877bdd329ca0c02bdd604817e7af36ad82f912132c50355af0920", "7600d4bb4e159b38408cb4f3a4fa19a5526eec0051c8c508ef1045f75b0f6083"))
