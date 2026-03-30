from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader


CHI_ORDER: List[str] = [
    "Tý",
    "Sửu",
    "Dần",
    "Mão",
    "Thìn",
    "Tị",
    "Ngọ",
    "Mùi",
    "Thân",
    "Dậu",
    "Tuất",
    "Hợi",
]


@dataclass
class QuanHanhKhien:
    chi: str
    vuong_hieu: str
    hanh_binh: str
    phan_quan: str


DEFAULT_QUAN_HANH_KHIEN: Dict[str, QuanHanhKhien] = {
    "Tý": QuanHanhKhien("Tý", "Chu Vương Hành Khiển", "Thiên Ôn hành binh chi thần", "Lý Tào phán quan"),
    "Sửu": QuanHanhKhien("Sửu", "Triệu Vương Hành Khiển", "Tam Thập Lục Thương hành binh chi thần", "Khúc Tào phán quan"),
    "Dần": QuanHanhKhien("Dần", "Ngụy Vương Hành Khiển", "Mộc Tinh hành binh chi thần", "Tiêu Tào phán quan"),
    "Mão": QuanHanhKhien("Mão", "Trịnh Vương Hành Khiển", "Thạch Tinh hành binh chi thần", "Liễu Tào phán quan"),
    "Thìn": QuanHanhKhien("Thìn", "Sở Vương Hành Khiển", "Hỏa Tinh hành binh chi thần", "Biểu Tào phán quan"),
    "Tị": QuanHanhKhien("Tị", "Ngô Vương Hành Khiển", "Thiên Hao hành binh chi thần", "Hứa Tào phán quan"),
    "Ngọ": QuanHanhKhien("Ngọ", "Tần Vương Hành Khiển", "Thiên Mã hành binh chi thần", "Ngọc Tào phán quan"),
    "Mùi": QuanHanhKhien("Mùi", "Tống Vương Hành Khiển", "Ngũ Đạo hành binh chi thần", "Lâm Tào phán quan"),
    "Thân": QuanHanhKhien("Thân", "Tề Vương Hành Khiển", "Ngũ Miếu hành binh chi thần", "Tống Tào phán quan"),
    "Dậu": QuanHanhKhien("Dậu", "Lỗ Vương Hành Khiển", "Ngũ Nhạc hành binh chi thần", "Cự Tào phán quan"),
    "Tuất": QuanHanhKhien("Tuất", "Việt Vương Hành Khiển", "Thiên Bá hành binh chi thần", "Thành Tào phán quan"),
    "Hợi": QuanHanhKhien("Hợi", "Lưu Vương Hành Khiển", "Ngũ Ôn hành binh chi thần", "Nguyễn Tào phán quan"),
}


DEFAULT_GIAO_THUA_TEMPLATE = """Nam mô A Di Đà Phật! (3 lần)

Con kính lạy:
- Hoàng thiên Hậu thổ chư vị Tôn thần
- Ngài Kim niên đương cai Thái Tuế chí đức Tôn thần
- Các ngài Bản cảnh Thành hoàng chư vị Đại vương
- Ngài Bản xứ Thần linh Thổ địa
- Ngài Định Phúc Táo quân

Hôm nay là {ngay_thang}
Tín chủ chúng con là: {ten_be}
Ngụ tại: {dia_chi}

Phút linh thiêng Giao thừa vừa tới, chúng con kính cẩn dâng hương hoa lễ vật,
nguyện nghênh tân, tiễn cựu, cầu cho gia đạo bình an, mọi sự cát tường.

Năm nay do:
{quan_hanh_khien}

Cúi xin chư vị Tôn thần chứng giám lòng thành, phù hộ độ trì.
Nam mô A Di Đà Phật! (3 lần)
"""


class VanKhanDatabase:
    def __init__(self, pdf_path: str | Path) -> None:
        self.pdf_path = Path(pdf_path)
        self._text_cache: str | None = None

    def _read_pdf_text(self) -> str:
        if self._text_cache is not None:
            return self._text_cache
        reader = PdfReader(str(self.pdf_path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        self._text_cache = "\n".join(pages)
        return self._text_cache

    def extract_quan_hanh_khien(self) -> Dict[str, QuanHanhKhien]:
        text = self._read_pdf_text()
        parsed: Dict[str, QuanHanhKhien] = {}

        for chi in CHI_ORDER:
            chi_pattern = "T[ịỵ]" if chi == "Tị" else re.escape(chi)
            pattern = (
                rf"Năm\s*{chi_pattern}\s*:\s*"
                r"(?P<vuong>[^,\n]+?)\s*,\s*"
                r"(?P<hanh>[^,\n]+?)\s*,\s*"
                r"(?P<phan>[^.\n]+?)\."
            )
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if not match:
                continue

            parsed[chi] = QuanHanhKhien(
                chi=chi,
                vuong_hieu=self._clean_cell(match.group("vuong")),
                hanh_binh=self._clean_cell(match.group("hanh")),
                phan_quan=self._clean_cell(match.group("phan")).replace("phản quan", "phán quan"),
            )

        # Bổ sung bằng dữ liệu chuẩn nếu PDF bị lỗi OCR/mất dấu.
        for chi, fallback_item in DEFAULT_QUAN_HANH_KHIEN.items():
            parsed.setdefault(chi, fallback_item)

        return parsed

    def get_quan_hanh_khien(self, year: int) -> QuanHanhKhien:
        data = self.extract_quan_hanh_khien()
        chi = CHI_ORDER[(year - 4) % 12]
        return data[chi]

    def extract_giao_thua_template(self) -> str:
        text = self._read_pdf_text()
        normalized = " ".join(text.split())
        marker = "Sơ khấn Giao thừa trong nhà"
        end_marker = "Văn khấn tạ năm mới"
        start = normalized.find(marker)
        end = normalized.find(end_marker)

        if start != -1 and end != -1 and end > start:
            section = normalized[start:end]
            section = section.replace("chúng con là :", "chúng con là: {ten_be}")
            section = section.replace("ngụ tại :", "ngụ tại: {dia_chi}")
            section = section.replace("Nay là giờ phút giao thừa năm", "Nay là {ngay_thang}, giờ phút giao thừa năm")
            return section

        return DEFAULT_GIAO_THUA_TEMPLATE

    def extract_prayers_catalog(self, limit: int | None = None) -> List[Dict[str, str]]:
        text = self._read_pdf_text().replace("\t", " ")
        text = re.sub(r"[ ]{2,}", " ", text)

        # Giữ cấu trúc dòng của PDF để form bài khấn sát bản gốc hơn.
        # Cải thiện pattern để nhận diện tiêu đề in đậm chính xác hơn
        heading_pattern = re.compile(
            r"^\s*(Văn\s+khấn[^:\n]{3,160})\s*$", 
            flags=re.IGNORECASE | re.MULTILINE
        )
        matches = list(heading_pattern.finditer(text))
        items: List[Dict[str, str]] = []
        seen_titles: set[str] = set()

        for idx, match in enumerate(matches):
            title = self._clean_heading(match.group(1))
            if not title or len(title) < 8:
                continue
            if "văn khấn" not in title.lower():
                continue
            # Loại bỏ các tiêu đề không phải là bài khấn chính
            if any(x in title.lower() for x in [
                "ra giấy thì đọc", "chúng tôi", "sau đây", "văn khấn:", 
                "nếu viết", "trong khi", "đứng trước", "xong hoá"
            ]):
                continue
            if title.lower() in seen_titles:
                continue

            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            
            # Kiểm tra xem nội dung có chứa dấu hiệu của bài khấn hợp lệ không
            if not self._is_valid_prayer_body(body):
                continue
                
            body = self._normalize_body_lines(body)
            body = self._inject_template_tokens(body)
            body = self._trim_body(body)

            if len(body) < 120:
                continue

            title = self._normalize_title(title)
            prayer_id = self._slugify(title.replace("Văn khấn", "").strip())
            prayer_id = prayer_id or f"bai_{len(items)+1}"
            seen_titles.add(title.lower())
            items.append({"id": prayer_id, "title": title, "template": body})

            if limit is not None and len(items) >= limit:
                break

        return items

    def export_seed_data(self, output_path: str | Path) -> None:
        quan_data = self.extract_quan_hanh_khien()
        payload = {
            "quan_hanh_khien": {chi: asdict(item) for chi, item in quan_data.items()},
            "giao_thua_template": self.extract_giao_thua_template(),
        }
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def export_prayers_catalog(self, output_path: str | Path, limit: int | None = None) -> None:
        prayers = self.extract_prayers_catalog(limit=limit)
        payload = {"Danh mục": prayers}
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _is_valid_prayer_body(body: str) -> bool:
        """
        Kiểm tra xem nội dung có phải là bài văn khấn hợp lệ không
        để tránh tách nhầm các phần không phải là bài khấn
        """
        if not body or len(body) < 50:
            return False
            
        body_lower = body.lower()
        
        # Các dấu hiệu của bài khấn hợp lệ
        prayer_indicators = [
            "nam mô", "con lạy", "kính lạy", "tín chủ", "chúng con",
            "ngụ tại", "hôm nay là", "cúi xin", "thành tâm",
            "a di đà phật", "phật", "thần", "thánh"
        ]
        
        # Phải có ít nhất 2 dấu hiệu của bài khấn
        indicator_count = sum(1 for indicator in prayer_indicators if indicator in body_lower)
        if indicator_count < 2:
            return False
            
        # Loại bỏ các nội dung không phải là bài khấn
        invalid_patterns = [
            "nếu viết văn khấn ra giấy thì đọc",
            "trong khi đợi tuần nhang",
            "đứng trước ngôi mộ và khấn",
            "xong hoá ngay cùng tiền vàng",
            "chúng tôi xin giới thiệu",
            "sau đây là nội dung"
        ]
        
        for pattern in invalid_patterns:
            if pattern in body_lower:
                return False
                
        return True

    @staticmethod
    def _clean_cell(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip(" -\n\t")

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", "_", value)
        return value.strip("_")

    @staticmethod
    def _clean_heading(value: str) -> str:
        value = re.sub(r"\s+", " ", value).strip(" -:;,.")
        value = re.sub(r"\b(Nam mô|Nam mo).*$", "", value, flags=re.IGNORECASE).strip()
        return value[:120]

    @staticmethod
    def _normalize_title(value: str) -> str:
        value = re.sub(r"\s+", " ", value).strip(" -:;,.")
        # Tránh tiêu đề quá dài do OCR dính nội dung mô tả.
        stop_words = [" Ý nghĩa", " Theo ", " Trong phong tục", " Cách tiến hành"]
        for stop in stop_words:
            pos = value.find(stop)
            if pos > 0:
                value = value[:pos].strip(" -:;,.")
        return value

    @staticmethod
    def _inject_template_tokens(value: str) -> str:
        value = re.sub(r"(?i)Tín chủ\s*(chúng\s*con|con)\s*là\s*:", "Tín chủ chúng con là: {ten_be}", value)
        value = re.sub(r"(?i)chúng\s*con\s*là\s*:", "chúng con là: {ten_be}", value)
        value = re.sub(r"(?i)ngụ\s*tại\s*:", "Ngụ tại: {dia_chi}", value)
        value = re.sub(r"(?i)hôm\s*nay\s*là\s*ngày", "Hôm nay là {ngay_thang}, ngày", value)
        return value

    @staticmethod
    def _trim_body(value: str) -> str:
        # Nếu nội dung quá ngắn, trả về nguyên bản
        if len(value) < 500:
            return value.strip()
            
        start_markers = ["Nam mô", "Nam mo", "Kính lạy", "Con kính lạy", "Tín chủ", "Hôm nay là"]
        start_pos = 0
        for marker in start_markers:
            pos = value.find(marker)
            if pos != -1:
                start_pos = pos
                break
        
        trimmed = value[start_pos:].strip()
        # Tăng giới hạn độ dài để không cắt mất nội dung
        return trimmed[:5000].strip()

    @staticmethod
    def _normalize_body_lines(value: str) -> str:
        lines = []
        for raw_line in value.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line:
                lines.append("")
                continue
            lines.append(line)
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    db = VanKhanDatabase(root / "vankhan.pdf")
    db.export_seed_data(root / "data" / "seed_data.json")
    db.export_prayers_catalog(root / "data" / "prayers.json")
    print("Đã trích xuất dữ liệu vào data/seed_data.json và data/prayers.json")
