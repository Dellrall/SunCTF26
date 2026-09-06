# Forensics & Steganography CTF Reference Guide

A rapid reference for file analysis, network packet inspection, memory dumps, and hidden data extraction.

---

## 1. Magic Bytes & File Headers Lookup

| Format | Header Bytes (Hex) | Trailer / Footer (Hex) |
| :--- | :--- | :--- |
| **PNG** | `89 50 4E 47 0D 0A 1A 0A` | `49 45 4E 44 AE 42 60 82` (`IEND`) |
| **JPEG** | `FF D8 FF` | `FF D9` |
| **GIF87a / GIF89a** | `47 49 46 38 37 61` / `47 49 46 38 39 61` | `00 3B` |
| **ZIP / DOCX / APK** | `50 4B 03 04` (or `50 4B 05 06` empty) | `50 4B 05 06` (End of Central Dir) |
| **GZIP** | `1F 8B 08` | — |
| **7Z** | `37 7A BC AF 27 1C` | — |
| **ELF Binary** | `7F 45 4C 46` (`\x7fELF`) | — |
| **PDF** | `25 50 44 46` (`%PDF`) | `25 25 45 4F 46` (`%%EOF`) |
| **PCAP** | `D4 C3 B2 A1` or `A1 B2 C3 D4` | — |
| **PCAPNG** | `0A 0D 0D 0A` | — |

---

## 2. File Triage & Carving Workflow

```bash
# 1. Inspect file identity & metadata
file suspicious_file
exiftool suspicious_file

# 2. Extract printable strings
strings -n 8 suspicious_file | grep -iE 'flag|pass|key|http|ctf|admin'

# 3. Detect embedded / appended files
binwalk -e -M suspicious_file
foremost -i suspicious_file -o output_carved/

# 4. Check for corrupted PNG chunks / size tampering (IHDR height fix)
pngcheck -v suspicious_file.png
```

---

## 3. Network Packet Analysis (`.pcap` / `.pcapng`)

### `tshark` Command Recipes

```bash
# Extract HTTP GET/POST URLs and User-Agents
tshark -r capture.pcap -Y "http.request" -T fields -e ip.src -e ip.dst -e http.request.method -e http.request.full_uri

# Export all exported HTTP objects / files
tshark -r capture.pcap --export-objects "http,./exported_http"

# Extract DNS query names (detect DNS tunneling / exfiltration)
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name | sort -u

# Extract ICMP payload data
tshark -r capture.pcap -Y "icmp" -T fields -e data.data | tr -d '\n' | xxd -r -p

# Follow TCP stream #0
tshark -r capture.pcap -z "follow,tcp,ascii,0" -q
```

### Python `scapy` Extraction Snippet
```python
from scapy.all import rdpcap, IP, TCP, Raw

packets = rdpcap("capture.pcap")
data_stream = b""
for pkt in packets:
    if pkt.haslayer(Raw):
        data_stream += pkt[Raw].load

print(f"[*] Total extracted raw bytes: {len(data_stream)}")
```

---

## 4. Steganography Techniques

### Image Steganography
- **PNG LSB & Alpha Planes**:
  ```bash
  zsteg -a image.png
  ```
- **JPEG Hidden Streams**:
  ```bash
  steghide extract -sf image.jpg
  stegseek image.jpg /usr/share/wordlists/rockyou.txt
  outguess -r image.jpg out.txt
  ```
- **Exif / Comment Metadata**: Check `exiftool`, `identify -verbose image.png`.

### Audio Steganography
- Open in **Audacity** / **Sonic Visualiser**:
  - Switch waveform to **Spectrogram view** (often reveals text or symbols drawn in frequency domain).
  - Check Morse code or DTMF tones (dual-tone multi-frequency phone keypad tones).

---

## 5. Memory Forensics (`volatility3`)

```bash
# Process list
python3 vol.py -f memdump.raw windows.pslist
python3 vol.py -f memdump.raw windows.pstree

# Dump specific process memory / executable
python3 vol.py -f memdump.raw windows.dumpfiles --pid <PID>

# Scan for command line arguments & console history
python3 vol.py -f memdump.raw windows.cmdline
python3 vol.py -f memdump.raw windows.consoles

# Scan for network connections
python3 vol.py -f memdump.raw windows.netscan

# Scan for passwords / hashes in memory
python3 vol.py -f memdump.raw windows.hashdump
python3 vol.py -f memdump.raw windows.lsadump
```
