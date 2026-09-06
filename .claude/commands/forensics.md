---
description: Digital forensics, packet extraction, file carving, and steganography analysis.
---

Analyze a digital forensics or steganography challenge.

### Diagnostic Checklist
1. **Magic Bytes / File Header**:
   - PNG: `89 50 4E 47`, JPEG: `FF D8 FF`, ZIP: `50 4B 03 04`, ELF: `7F 45 4C 46`, PDF: `25 50 44 46`.
2. **Carving & Strings**:
   - `file <artifact>`, `exiftool <artifact>`, `strings -n 8 <artifact> | grep -iE 'flag|ctf|key'`.
   - `binwalk -e -M <artifact>`, `foremost -i <artifact>`.
3. **PCAP Analysis**:
   - Export HTTP objects: `tshark -r <pcap> --export-objects "http,./extracted"`.
   - Extract DNS queries: `tshark -r <pcap> -Y "dns.flags.response == 0" -T fields -e dns.qry.name`.
4. **Steganography**:
   - PNG LSB: `zsteg -a image.png`.
   - JPEG: `steghide extract -sf image.jpg`, `stegseek image.jpg /usr/share/wordlists/rockyou.txt`.
   - Audio: Spectrogram view in Audacity / Sonic Visualiser.
