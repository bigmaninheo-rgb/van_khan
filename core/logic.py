from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Simple lunar date calculation for web (placeholder)
def simple_lunar_date(solar_date: datetime) -> str:
    """Simple lunar date calculation for web version"""
    # This is a simplified version - in production, use proper lunar calendar
    lunar_months = ["Giêng", "Hai", "Ba", "Tư", "Năm", "Sáu", "Bảy", "Tám", "Chín", "Mười", "Một", "Chạp"]
    lunar_day = (solar_date.day + 10) % 30 + 1  # Simplified calculation
    lunar_month_idx = (solar_date.month - 1) % 12
    lunar_year = solar_date.year
    
    return f"ngày {lunar_day:02d}/{lunar_month_idx + 1:02d}/{lunar_year} (Âm lịch)"

from data.sqlite_db import get_quan_hanh_khien_from_db, init_database

# Cache cho Quan Hành Khiên để không đọc database nhiều lần
_quan_hanh_khien_cache: Dict[int, str] = {}

# Cache cho personalize_prayer để không xử lý lại cùng một bài
_prayer_cache: Dict[str, str] = {}

# Khởi tạo database
try:
    init_database()
except Exception as e:
    print(f"Lỗi khởi tạo database: {e}")



def build_quan_hanh_khien_text(year: int) -> str:
    # Kiểm tra cache trước
    if year in _quan_hanh_khien_cache:
        return _quan_hanh_khien_cache[year]
    
    # Lấy từ database
    quan_data = get_quan_hanh_khien_from_db(year)
    if quan_data:
        result = f"{quan_data.vuong_hieu}, {quan_data.hanh_binh}, {quan_data.phan_quan}."
    else:
        result = "Quan Hành Khiên không có sẵn"
    
    # Lưu vào cache
    _quan_hanh_khien_cache[year] = result
    return result


def build_lunar_date_text(solar_date: datetime | None = None) -> str:
    date_obj = solar_date or datetime.now()
    return simple_lunar_date(date_obj)


def extract_prayer_only(template: str) -> str:
    """
    Extract only the prayer text part from a template, excluding Ý nghĩa and Sắm lễ sections.
    """
    lines = template.split('\n')
    prayer_lines = []
    in_prayer = False
    
    for line in lines:
        line = line.strip()
        # Skip Ý nghĩa and Sắm lễ sections
        if line.startswith('Ý nghĩa:') or line.startswith('Sắm lễ:'):
            in_prayer = False
            continue
        
        # Start capturing when we see prayer patterns
        if (line.startswith('Nam mô') or 
            line.startswith('- Con lạy') or 
            line.startswith('Hôm nay là') or
            line.startswith('Tín chủ') or
            'Nam mô a di Đà Phật!' in line):
            in_prayer = True
        
        if in_prayer:
            prayer_lines.append(line)
    
    # If no prayer was found, return the original template
    if not prayer_lines:
        return template
    
    return '\n'.join(prayer_lines)


def personalize_prayer(
    template: str,
    ten_be: str,
    dia_chi: str,
    ngay_thang: str | None = None,
    ngay_am_lich: str | None = None,
    year: int | None = None,
    prayer_only: bool = False,
) -> str:
    # Set defaults quickly
    if ngay_thang is None:
        ngay_thang = datetime.now().strftime("ngày %d/%m/%Y")
    if ngay_am_lich is None:
        ngay_am_lich = build_lunar_date_text()
    if year is None:
        year = datetime.now().year

    # Create cache key based on all inputs
    cache_key = f"{hash(template)}_{ten_be}_{dia_chi}_{ngay_thang}_{ngay_am_lich}_{year}_{prayer_only}"
    
    # Check cache first
    if cache_key in _prayer_cache:
        return _prayer_cache[cache_key]

    # Extract prayer only if requested (this is fast)
    if prayer_only:
        template = extract_prayer_only(template)

    # Get quan text from cache (this is now fast)
    quan_text = build_quan_hanh_khien_text(year=year)
    
    # Prepare replacement values
    replacements = {
        'ten_be': ten_be.strip() or "........................",
        'dia_chi': dia_chi.strip() or "........................",
        'ngay_thang': ngay_thang.strip(),
        'ngay_am_lich': ngay_am_lich.strip(),
        'quan_hanh_khien': quan_text,
    }
    
    # Fast string replacement using format method
    try:
        result = template.format(**replacements)
    except KeyError:
        # If template doesn't have expected placeholders, return original
        result = template
    
    # Cache the result
    _prayer_cache[cache_key] = result
    
    return result


def clear_prayer_cache() -> None:
    """Xóa cache để giải phóng bộ nhớ khi cần"""
    global _prayer_cache, _quan_hanh_khien_cache
    _prayer_cache.clear()
    _quan_hanh_khien_cache.clear()
