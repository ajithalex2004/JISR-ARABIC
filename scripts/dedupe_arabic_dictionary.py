import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/src/services/arabicDictionary.ts', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'const ARABIC_DICTIONARY: Record<string, WordDefinition> = {' in line:
        start_idx = i
    elif start_idx != -1 and line.strip().startswith('};') and end_idx == -1:
        end_idx = i
        break

print(f"ARABIC_DICTIONARY found from line {start_idx + 1} to {end_idx + 1}")

dict_lines = lines[start_idx + 1:end_idx]
seen_keys = set()
deduped_lines = []

# Process in reverse so newer/more specific entries take precedence, or process forward?
# Let's inspect duplicate keys:
key_regex = re.compile(r"^\s*'([^']+)'\s*:")

# Collect entries preserving last occurrence
entries_map = {}
other_lines = []

for line in dict_lines:
    m = key_regex.match(line)
    if m:
        key = m.group(1)
        entries_map[key] = line
    elif line.strip().startswith('//'):
        # Keep comments
        other_lines.append(line)

print(f"Total unique keys: {len(entries_map)}")

new_dict_lines = []
for k in sorted(entries_map.keys()):
    new_dict_lines.append(entries_map[k])

final_lines = lines[:start_idx + 1] + new_dict_lines + lines[end_idx:]

with open('frontend/src/services/arabicDictionary.ts', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("Successfully deduplicated ARABIC_DICTIONARY in arabicDictionary.ts!")
