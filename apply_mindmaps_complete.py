# -*- coding: utf-8 -*-
"""
Builder and Patcher for Mindmaps in Flutter Mobile App.
Aligns Concept Mindmaps (Tab 1), Syntax Flowcharts (Tab 2), and Grammar Rules (Tab 3)
across all grades (Grade 1 to 12).
"""
import re
import sys
import os

target_path = r"c:\JISR ARABIC\mobile\lib\screens\mindmap_screen.dart"

with open(target_path, "r", encoding="utf-8") as f:
    text = f.read()

# ---------------------------------------------------------------------------
# 1. Update MindmapsScreen Widget constructor and fields
# ---------------------------------------------------------------------------
old_widget_class = """class MindmapsScreen extends StatefulWidget {
  final bool isArabic;
  final int initialGrade;
  final Function(String text)? onVocalize;
  final Function(String query)? onAskFahim;
  final VoidCallback onBack;

  const MindmapsScreen({
    super.key,
    required this.isArabic,
    this.initialGrade = 5,
    this.onVocalize,
    this.onAskFahim,
    required this.onBack,
  });"""

new_widget_class = """class MindmapsScreen extends StatefulWidget {
  final bool isArabic;
  final int initialGrade;
  final dynamic api;
  final String? token;
  final ValueChanged<int>? onGradeChanged;
  final Function(String text)? onVocalize;
  final Function(String query)? onAskFahim;
  final VoidCallback onBack;

  const MindmapsScreen({
    super.key,
    required this.isArabic,
    this.initialGrade = 5,
    this.api,
    this.token,
    this.onGradeChanged,
    this.onVocalize,
    this.onAskFahim,
    required this.onBack,
  });"""

if old_widget_class in text:
    text = text.replace(old_widget_class, new_widget_class, 1)
    print("Updated MindmapsScreen widget constructor.")
else:
    print("Error: Could not find old_widget_class in text!")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Extract _chapters block and convert it to _grade5Chapters
# ---------------------------------------------------------------------------
ch_idx = text.find("final List<Map<String, dynamic>> _chapters = [")
if ch_idx == -1:
    print("Error: Could not find _chapters declaration!")
    sys.exit(1)

# Find start of comment before it
c_idx = text.rfind("//", 0, ch_idx)
ch_start = c_idx if c_idx != -1 and (ch_idx - c_idx < 100) else ch_idx

init_state_idx = text.find("@override\n  void initState()", ch_start)
if init_state_idx == -1:
    init_state_idx = text.find("@override\r\n  void initState()", ch_start)
if init_state_idx == -1:
    print("Error: Could not find initState after _chapters!")
    sys.exit(1)

ch_end = text.rfind(";", ch_start, init_state_idx) + 1
original_ch_code = text[ch_start:ch_end]

# Rename declaration to static final List<Map<String, dynamic>> _grade5Chapters = [
grade5_chapters_code = re.sub(
    r"final List<Map<String, dynamic>> _chapters\s*=\s*\[",
    "static final List<Map<String, dynamic>> _grade5Chapters = [",
    original_ch_code
)

# ---------------------------------------------------------------------------
# 3. Read extra chapters from patch_mindmaps.py (Grades 1-4, 9-12)
# ---------------------------------------------------------------------------
p1_path = r"C:\Users\athom\.gemini\antigravity\brain\7ef9b81c-cec0-44be-8ab1-7224e2126571\scratch\patch_mindmaps.py"
p1_text = open(p1_path, "r", encoding="utf-8").read()
m_extra = re.search(r"extra_chapters = '''(.*?)'''", p1_text, re.DOTALL)
if not m_extra:
    print("Error: Could not extract extra_chapters from patch_mindmaps.py!")
    sys.exit(1)
extra_chapters_code = m_extra.group(1).strip()

# ---------------------------------------------------------------------------
# 4. Generate _grade6Chapters, _grade7Chapters, _grade8Chapters from frontend
# ---------------------------------------------------------------------------
VALID_KEYS = [
    'id', 'titleAr', 'titleEn', 'unitAr', 'unitEn', 'pages', 'color', 
    'summaryAr', 'summaryEn', 'branches', 'items', 'ar', 'en', 
    'root', 'pattern', 'meaningAr', 'meaningEn', 'icon'
]

def convert_ts_chapters_to_dart(ts_content, var_name):
    # Strip export statement
    body = re.sub(r'export const \w+:\s*\w+\[\]\s*=\s*', '', ts_content).strip()
    if body.endswith(';'):
        body = body[:-1].strip()

    # Convert hex colors '#2563EB' -> const Color(0xFF2563EB)
    body = re.sub(r"'#([0-9a-fA-F]{6})'", lambda m: f"const Color(0xFF{m.group(1).upper()})", body)

    # Quote ONLY valid schema keys to avoid breaking words like "Values:" or "Flag:"
    for k in VALID_KEYS:
        # Match word preceded by space or { or newline and followed by colon
        body = re.sub(r"([{,\s\n])\b" + k + r"\b\s*:", r"\1'" + k + "':", body)

    # Insert 'icon': Icons.auto_stories_rounded in chapter maps after 'pages': ...
    body = re.sub(r"('pages':\s*'[^']+',)", r"\1\n    'icon': Icons.auto_stories_rounded,", body)

    # Insert 'icon': Icons.menu_book_rounded only in branch maps (preceded by 6-8 spaces indentation)
    body = re.sub(r"(\n\s{6,8}'titleEn':\s*'[^']+',)", r"\1\n        'icon': Icons.menu_book_rounded,", body)

    return f"  // {var_name}\n  static final List<Map<String, dynamic>> {var_name} = " + body + ";\n"

g6_ts = open("scratch_g6.ts", "r", encoding="utf-8").read()
g7_ts = open("scratch_g7.ts", "r", encoding="utf-8").read()
g8_ts = open("scratch_g8.ts", "r", encoding="utf-8").read()

g6_dart = convert_ts_chapters_to_dart(g6_ts, "_grade6Chapters")
g7_dart = convert_ts_chapters_to_dart(g7_ts, "_grade7Chapters")
g8_dart = convert_ts_chapters_to_dart(g8_ts, "_grade8Chapters")

# ---------------------------------------------------------------------------
# 5. Build State Variables & Chapter loading helpers
# ---------------------------------------------------------------------------
state_logic = """  List<Map<String, dynamic>> _chapters = [];

  static List<Map<String, dynamic>> _getFallbackChapters(int grade) {
    switch (grade) {
      case 1:
        return _grade1Chapters;
      case 2:
        return _grade2Chapters;
      case 3:
        return _grade3Chapters;
      case 4:
        return _grade4Chapters;
      case 6:
        return _grade6Chapters;
      case 7:
        return _grade7Chapters;
      case 8:
        return _grade8Chapters;
      case 9:
        return _grade9Chapters;
      case 10:
        return _grade10Chapters;
      case 11:
        return _grade11Chapters;
      case 12:
        return _grade12Chapters;
      case 5:
      default:
        return _grade5Chapters;
    }
  }

  static List<Map<String, dynamic>> _castMapList(dynamic list) {
    if (list is! List) return [];
    return list.map((item) {
      if (item is Map) {
        final map = Map<String, dynamic>.from(item);
        if (map['branches'] is List) {
          map['branches'] = (map['branches'] as List).map((b) {
            if (b is Map) {
              final bMap = Map<String, dynamic>.from(b);
              if (bMap['items'] is List) {
                bMap['items'] = (bMap['items'] as List).map((it) => it is Map ? Map<String, dynamic>.from(it) : <String, dynamic>{}).toList();
              }
              if (bMap['color'] is String) {
                bMap['color'] = _parseColor(bMap['color'] as String);
              }
              return bMap;
            }
            return <String, dynamic>{};
          }).toList();
        }
        if (map['color'] is String) {
          map['color'] = _parseColor(map['color'] as String);
        }
        map['icon'] ??= Icons.auto_stories_rounded;
        return map;
      }
      return <String, dynamic>{};
    }).toList();
  }

  static Color _parseColor(String? colorStr) {
    if (colorStr == null || colorStr.isEmpty) return const Color(0xFF2563EB);
    try {
      final hex = colorStr.replaceAll('#', '');
      if (hex.length == 6) {
        return Color(int.parse('FF$hex', radix: 16));
      }
    } catch (_) {}
    return const Color(0xFF2563EB);
  }

  @override
  void initState() {
    super.initState();
    _selectedGrade = widget.initialGrade;
    _tabController = TabController(length: 3, vsync: this);
    _loadChaptersForGrade(_selectedGrade);
  }

  @override
  void didUpdateWidget(covariant MindmapsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialGrade != oldWidget.initialGrade && widget.initialGrade != _selectedGrade) {
      _loadChaptersForGrade(widget.initialGrade);
    }
  }

  void _loadChaptersForGrade(int grade) async {
    setState(() {
      _selectedGrade = grade;
      _selectedChapterIndex = 0;
      _chapters = _getFallbackChapters(grade);
    });

    if (widget.api != null) {
      try {
        final res = await widget.api.mindmaps(grade: grade, term: 1, token: widget.token);
        if (res != null && res['chapters'] is List && (res['chapters'] as List).isNotEmpty && mounted) {
          final live = _castMapList(res['chapters']);
          if (live.isNotEmpty) {
            setState(() {
              _chapters = live;
              if (_selectedChapterIndex >= _chapters.length) {
                _selectedChapterIndex = 0;
              }
            });
          }
        }
      } catch (err) {
        debugPrint('Failed to fetch remote mindmaps for grade $grade: $err');
      }
    }
  }

  void _showGradePicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.isArabic ? 'اختر الصف الدراسي (Select Grade)' : 'Select Grade (اختر الصف)',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) {
                  final isSel = g == _selectedGrade;
                  return ChoiceChip(
                    label: Text(widget.isArabic ? 'الصف $g' : 'Grade $g'),
                    selected: isSel,
                    selectedColor: const Color(0xFF6C5CE7),
                    labelStyle: TextStyle(
                      color: isSel ? Colors.white : const Color(0xFF334155),
                      fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                    ),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(ctx);
                        _loadChaptersForGrade(g);
                        widget.onGradeChanged?.call(g);
                      }
                    },
                  );
                }).toList(),
              ),
            ],
          ),
        );
      },
    );
  }
"""

# Find end of initState in original text
init_end_idx = text.find("}", init_state_idx) + 1

replacement_chapters_and_state = (
    grade5_chapters_code + "\n\n" +
    g6_dart + "\n\n" +
    g7_dart + "\n\n" +
    g8_dart + "\n\n" +
    extra_chapters_code + "\n\n" +
    state_logic
)

text = text[:ch_start] + replacement_chapters_and_state + text[init_end_idx:]
print("Replaced chapters and state methods successfully.")

# ---------------------------------------------------------------------------
# 6. Update build() method safety for activeChapter
# ---------------------------------------------------------------------------
old_build_start = "    final activeChapter = _chapters[_selectedChapterIndex];"
new_build_start = """    if (_chapters.isEmpty) {
      _chapters = _getFallbackChapters(_selectedGrade);
    }
    if (_selectedChapterIndex >= _chapters.length) {
      _selectedChapterIndex = 0;
    }
    final activeChapter = _chapters.isNotEmpty ? _chapters[_selectedChapterIndex] : _grade5Chapters[0];"""

if old_build_start in text:
    text = text.replace(old_build_start, new_build_start, 1)
    print("Made activeChapter access safe in build().")
else:
    print("Warning: old_build_start not found in text.")

# ---------------------------------------------------------------------------
# 7. Update _buildSelectorHeader() to display dynamic grade and open grade picker
# ---------------------------------------------------------------------------
old_header_block = """                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.school_rounded, color: Color(0xFF6C5CE7), size: 15),
                      const SizedBox(width: 6),
                      Text(
                        widget.isArabic ? 'الصَّفُّ: الخَامِسُ (Class 5)' : 'Class: Grade 5',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF6C5CE7),
                        ),
                      ),
                    ],
                  ),"""

new_header_block = """                  child: InkWell(
                    onTap: () => _showGradePicker(context),
                    borderRadius: BorderRadius.circular(20),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.school_rounded, color: Color(0xFF6C5CE7), size: 15),
                          const SizedBox(width: 6),
                          Text(
                            widget.isArabic ? 'الصَّفُّ: $_selectedGrade (Class $_selectedGrade)' : 'Class: Grade $_selectedGrade',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF6C5CE7),
                            ),
                          ),
                          const SizedBox(width: 4),
                          const Icon(Icons.arrow_drop_down_rounded, color: Color(0xFF6C5CE7), size: 18),
                        ],
                      ),
                    ),
                  ),"""

if old_header_block in text:
    text = text.replace(old_header_block, new_header_block, 1)
    print("Updated grade selector header to be interactive and dynamic.")
else:
    print("Warning: old_header_block not found in text.")

# ---------------------------------------------------------------------------
# 8. Replace Tab 2 with Grade-Adaptive Syntax Flowcharts
# ---------------------------------------------------------------------------
p2_path = r"C:\Users\athom\.gemini\antigravity\brain\7ef9b81c-cec0-44be-8ab1-7224e2126571\scratch\patch_mindmaps_phase2.py"
p2_text = open(p2_path, "r", encoding="utf-8").read()
m_tab2 = re.search(r"tab2_code = '''(.*?)'''", p2_text, re.DOTALL)
if not m_tab2:
    print("Error: Could not extract tab2_code from patch_mindmaps_phase2.py!")
    sys.exit(1)
tab2_replacement = m_tab2.group(1).strip()

tab2_marker = "// TAB 2: SYNTAX & GRAMMAR DECISION FLOWCHART"
tab2_idx = text.find(tab2_marker)
flow_node_marker = "Widget _buildFlowNode({"
flow_node_idx = text.find(flow_node_marker, tab2_idx)

if tab2_idx != -1 and flow_node_idx != -1:
    text = text[:tab2_idx] + tab2_replacement + "\n\n  " + text[flow_node_idx:]
    print("Replaced Tab 2 with grade-adaptive syntax flowcharts.")
else:
    print("Error: Could not find markers for Tab 2 replacement!")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 9. Replace Tab 3 with Grade-Adaptive Grammar Rules
# ---------------------------------------------------------------------------
p3_path = r"C:\Users\athom\.gemini\antigravity\brain\7ef9b81c-cec0-44be-8ab1-7224e2126571\scratch\patch_mindmaps_phase3.py"
p3_text = open(p3_path, "r", encoding="utf-8").read()
m_rules = re.search(r"rules_helper = '''(.*?)'''", p3_text, re.DOTALL)
if not m_rules:
    print("Error: Could not extract rules_helper from patch_mindmaps_phase3.py!")
    sys.exit(1)
rules_helper_code = m_rules.group(1).strip()

rules_tab_marker = "Widget _buildCurriculumRulesTab() {"
rules_tab_idx = text.find(rules_tab_marker)
listview_marker = "return ListView("
listview_idx = text.find(listview_marker, rules_tab_idx)

if rules_tab_idx != -1 and listview_idx != -1:
    new_rules_head = """Widget _buildCurriculumRulesTab() {
    final rules = _getCurriculumRulesForGrade(_selectedGrade);
    if (rules.isNotEmpty && !rules.any((r) => r['key'] == _selectedGrammarTopicKey)) {
      _selectedGrammarTopicKey = rules.first['key'] as String;
    }

    """
    text = text[:rules_tab_idx] + new_rules_head + text[listview_idx:]
    print("Replaced Tab 3 method header.")
else:
    print("Error: Could not find Tab 3 method markers!")
    sys.exit(1)

# Append rules_helper_code right before the last closing brace of the State class
last_brace = text.rfind("}")
if last_brace != -1:
    text = text[:last_brace] + "\n  " + rules_helper_code + "\n}\n"
    print("Appended rules helper and static rule sets before closing brace.")
else:
    print("Error: Could not find last brace!")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 10. Write to target file
# ---------------------------------------------------------------------------
with open(target_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Successfully patched {target_path}!")
