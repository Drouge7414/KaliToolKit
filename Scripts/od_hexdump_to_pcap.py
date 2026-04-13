#!/usr/bin/env python3
# od_hexdump_to_pcap.py
#
# Converts an `od` (octal dump) formatted hex dump back into a valid pcap file.
#
# Use when you have a hex dump generated with:
#   od -A o -t x2 capture.pcap > dump.txt
#
# The od tool outputs 16-bit words in native (little-endian) byte order with
# octal offsets. This script skips the offset column and swaps each word's
# bytes back to the correct order before writing the binary pcap file.
#
# Usage:
#   python3 od_hexdump_to_pcap.py
#   (edit dump.txt and capture.pcap filenames below as needed)
#
# Output can be opened directly in Wireshark.


import re

with open('dnsqr.dump', 'r') as f:
    content = f.read()

raw = bytearray()

for line in content.strip().split('\n'):
    parts = line.split()
    if not parts:
        continue
    # Skip the octal offset, grab the hex words
    words = parts[1:]
    for word in words:
        if re.match(r'^[0-9a-f]{4}$', word):
            # od swaps bytes in each 16-bit word, swap them back
            raw.append(int(word[2:4], 16))
            raw.append(int(word[0:2], 16))

with open('capture.pcap', 'wb') as f:
    f.write(raw)

print(f"Written {len(raw)} bytes")
