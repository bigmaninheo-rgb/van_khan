"""
khan_parser.py - Đọc file khan.txt và nạp vào SQLite database.
Sử dụng single-pass để đọc nhanh, không quét lại file nhiều lần.
"""
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
TEXT_PATH = ROOT / "khan.txt"
DB_PATH = ROOT / "data" / "vankhan.db"

CHAPTER_NAMES = {
    "I":   "Mừng thọ, Cưới hỏi, Sinh dưỡng",
    "II":  "Tang, Giỗ tổ tiên",
    "III": "Tết Nguyên Đán",
    "IV":  "Rằm, Mồng 1 và các ngày lễ khác",
    "V":   "Lễ chùa, Đình, Miếu",
    "VI":  "Làm nhà, Chuyển nhà, Tân gia, Khai trương",
}

# Pattern nhận diện dòng tiêu đề chương trong mục lục: "I. VĂN CÚNG..."
RE_CHAPTER = re.compile(r'^(I|II|III|IV|V|VI)\.\s+VĂN CÚNG', re.IGNORECASE)
# Pattern nhận diện mục trong mục lục: "1. Văn cúng ... 7" (có số trang ở cuối)
RE_TOC_ITEM = re.compile(r'^(\d+)\.\s+(Văn\s+cúng.*?)\s*[…\.]+\s*(\d+)\s*$', re.IGNORECASE)
# Pattern nhận diện tiêu đề bài viết trong phần nội dung: "1. Văn cúng ..."
RE_ARTICLE_TITLE = re.compile(r'^(\d+)\.\s+(Văn\s+c[úu]ng.*)$', re.IGNORECASE)
# Dòng phân cách chương
RE_SEPARATOR = re.compile(r'^={10,}')


def parse_khan_txt() -> List[Dict[str, Any]]:
    """
    Đọc khan.txt một lần, tìm mục lục rồi trích xuất nội dung từng bài.
    """
    if not TEXT_PATH.exists():
        print(f"❌ Không tìm thấy: {TEXT_PATH}")
        return []

    lines = TEXT_PATH.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    print(f"📄 Đã đọc file: {total_lines} dòng")

    # ── BƯỚC 1: Quét mục lục (PASS 1) ──────────────────────────────────────
    # Mục lục nằm trong đoạn đầu file, trước dấu === đầu tiên dài
    toc_items: List[Dict[str, Any]] = []
    current_chapter = ""
    in_toc = True  # Giả sử mục lục ở đầu file

    for lineno, raw in enumerate(lines):
        line = raw.strip()

        # Khi gặp dấu === lần đầu, coi như hết mục lục; các === sau là phân chương
        if RE_SEPARATOR.match(line):
            if in_toc:
                in_toc = False
            continue

        if in_toc:
            chap_m = RE_CHAPTER.match(line)
            if chap_m:
                current_chapter = chap_m.group(1).upper()
                continue

            toc_m = RE_TOC_ITEM.match(line)
            if toc_m and current_chapter:
                toc_items.append({
                    "number": int(toc_m.group(1)),
                    "title":  toc_m.group(2).strip(),
                    "chapter": current_chapter,
                })

    print(f"📋 Mục lục: tìm thấy {len(toc_items)} bài")

    if not toc_items:
        print("❌ Không tìm thấy bài nào trong mục lục!")
        return []

    # ── BƯỚC 2: Xây dựng index vị trí tiêu đề trong phần nội dung (PASS 2) ──
    # Map: (number, title_prefix) -> line_start_in_content
    # Phần nội dung bắt đầu từ sau === đầu tiên
    content_start_line = 0
    for i, raw in enumerate(lines):
        if RE_SEPARATOR.match(raw.strip()):
            content_start_line = i + 1
            break

    # Tạo lookup nhanh: number -> line index bắt đầu (trong phần nội dung)
    number_to_linestart: Dict[int, int] = {}
    for i in range(content_start_line, total_lines):
        m = RE_ARTICLE_TITLE.match(lines[i].strip())
        if m:
            num = int(m.group(1))
            # Chỉ ghi lần đầu gặp số này (tránh trùng lặp nếu có)
            if num not in number_to_linestart:
                number_to_linestart[num] = i

    print(f"🔍 Đã index {len(number_to_linestart)} tiêu đề bài trong phần nội dung")

    # ── BƯỚC 3: Trích xuất nội dung từng bài ────────────────────────────────
    prayers: List[Dict[str, Any]] = []
    for idx, item in enumerate(toc_items):
        num = item["number"]
        title = item["title"]
        chapter = item["chapter"]

        start_line = number_to_linestart.get(num)
        if start_line is None:
            print(f"   ⚠️  [{idx+1}] Không tìm thấy nội dung bài {num}: {title}")
            prayers.append({
                "id": f"{chapter}_{idx+1:03d}",
                "title": title,
                "template": f"(Nội dung bài \"{title}\" chưa được tìm thấy.)"
            })
            continue

        # Tìm điểm kết thúc: bài tiếp theo hoặc dấu ===
        end_line = total_lines
        next_num = toc_items[idx + 1]["number"] if idx + 1 < len(toc_items) else None

        for j in range(start_line + 1, total_lines):
            stripped = lines[j].strip()
            # Gặp === là kết thúc
            if RE_SEPARATOR.match(stripped):
                end_line = j
                break
            # Gặp tiêu đề bài tiếp theo là kết thúc
            if next_num and RE_ARTICLE_TITLE.match(stripped):
                m2 = RE_ARTICLE_TITLE.match(stripped)
                if m2 and int(m2.group(1)) == next_num:
                    end_line = j
                    break

        # Ghép nội dung, bỏ dòng tiêu đề (dòng đầu = tiêu đề bài)
        content_lines = lines[start_line + 1: end_line]
        content = "\n".join(content_lines).strip()
        # Rút gọn dòng trống liên tiếp
        content = re.sub(r'\n{3,}', '\n\n', content)

        prayers.append({
            "id": f"{chapter}_{idx+1:03d}",
            "title": title,
            "template": content,
        })
        print(f"   ✅ [{idx+1}/{len(toc_items)}] {title[:50]}")

    return prayers


def normalize_template(template: str) -> str:
    """
    Chuẩn hóa template: thay thế ... bằng placeholders
    """
    import re
    
    # Thay thế các pattern cụ thể trước
    template = re.sub(r'Hôm nay là ngày\s*…\s*tháng\s*…\s*năm\s*…', 'Hôm nay là {ngay_thang}', template, flags=re.IGNORECASE)
    template = re.sub(r'ngày\s*…\s*tháng\s*…\s*năm\s*…', '{ngay_thang}', template, flags=re.IGNORECASE)
    template = re.sub(r'Vợ chồng con là\s*…', 'Vợ chồng con là {ten_be}', template, flags=re.IGNORECASE)
    template = re.sub(r'tên là\s*…', 'tên là {ten_be}', template, flags=re.IGNORECASE)
    template = re.sub(r'ngụ tại\s*…', 'ngụ tại {dia_chi}', template, flags=re.IGNORECASE)
    template = re.sub(r'tại\s*…', 'tại {dia_chi}', template, flags=re.IGNORECASE)
    
    # Thêm ngày âm lịch sau ngày dương lịch
    template = re.sub(r'(Hôm nay là \{ngay_thang\})', r'\1\nNgày âm lịch: {ngay_am_lich}', template, flags=re.IGNORECASE)
    
    # Thay thế tất cả … còn lại
    template = re.sub(r'…', '{ten_be}', template, flags=re.IGNORECASE)
    
    return template


def init_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prayers (
            id       TEXT PRIMARY KEY,
            title    TEXT,
            template TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quan_hanh_khien (
            year       INTEGER PRIMARY KEY,
            vong_hieu  TEXT,
            hanh_binh  TEXT,
            phan_quan  TEXT
        )
    ''')
    conn.commit()
    conn.close()


def load_prayers_from_txt() -> None:
    print("\n" + "=" * 50)
    print("NẠP DỮ LIỆU TỪ KHAN.TXT → SQLITE")
    print("=" * 50)

    init_database()
    prayers = parse_khan_txt()

    if not prayers:
        print("❌ Không có bài nào để lưu.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM prayers")
    
    # Chuẩn hóa template trước khi lưu
    normalized_prayers = []
    for p in prayers:
        normalized = p.copy()
        normalized["template"] = normalize_template(p["template"])
        normalized_prayers.append(normalized)
    
    conn.executemany(
        "INSERT INTO prayers (id, title, template) VALUES (?, ?, ?)",
        [(p["id"], p["title"], p["template"]) for p in normalized_prayers],
    )
    conn.commit()
    conn.close()

    print("\n" + "=" * 50)
    print(f"✅ XONG! Đã lưu {len(prayers)} bài vào: {DB_PATH}")
    print("=" * 50)


def get_prayers_from_db() -> List[Dict[str, Any]]:
    """Lấy danh sách bài từ database (dùng trong app)."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, title, template FROM prayers").fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "template": r[2]} for r in rows]


if __name__ == "__main__":
    load_prayers_from_txt()
