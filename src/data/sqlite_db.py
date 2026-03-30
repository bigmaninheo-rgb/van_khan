import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import asdict

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data.database import VanKhanDatabase, QuanHanhKhien

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "vankhan.db"


def init_database() -> None:
    """Khởi tạo database SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng Quan Hành Khiên
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quan_hanh_khien (
            year INTEGER PRIMARY KEY,
            vong_hieu TEXT,
            hanh_binh TEXT,
            phan_quan TEXT
        )
    ''')
    
    # Tạo bảng prayers catalog
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prayers (
            id TEXT PRIMARY KEY,
            title TEXT,
            template TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def save_quan_hanh_khien_to_db(year: int, data: QuanHanhKhien) -> None:
    """Lưu Quan Hành Khiên vào database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO quan_hanh_khien (year, vong_hieu, hanh_binh, phan_quan)
        VALUES (?, ?, ?, ?)
    ''', (year, data.vuong_hieu, data.hanh_binh, data.phan_quan))
    
    conn.commit()
    conn.close()


def get_quan_hanh_khien_from_db(year: int) -> QuanHanhKhien | None:
    """Lấy Quan Hành Khiên từ database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT vong_hieu, hanh_binh, phan_quan 
        FROM quan_hanh_khien 
        WHERE year = ?
    ''', (year,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return QuanHanhKhien(chi="", vuong_hieu=row[0], hanh_binh=row[1], phan_quan=row[2])
    return None


def save_prayers_to_db(prayers: List[Dict[str, Any]]) -> None:
    """Lưu danh sách prayers vào database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM prayers')  # Xóa dữ liệu cũ
    
    for prayer in prayers:
        cursor.execute('''
            INSERT INTO prayers (id, title, template)
            VALUES (?, ?, ?)
        ''', (prayer['id'], prayer['title'], prayer['template']))
    
    conn.commit()
    conn.close()


def get_prayers_from_db() -> List[Dict[str, Any]]:
    """Lấy danh sách prayers từ database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, title, template FROM prayers')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {'id': row[0], 'title': row[1], 'template': row[2]}
        for row in rows
    ]


def populate_database_from_pdf(pdf_path: Path) -> None:
    """Điền dữ liệu vào database từ PDF (chỉ chạy một lần)"""
    print("Đang khởi tạo database từ PDF...")
    
    # Khởi tạo database
    init_database()
    
    # Đọc dữ liệu từ PDF
    db = VanKhanDatabase(pdf_path)
    
    # Lưu Quan Hành Khiên cho các năm phổ biến
    for year in range(2020, 2031):
        try:
            quan_data = db.get_quan_hanh_khien(year)
            save_quan_hanh_khien_to_db(year, quan_data)
            print(f"Đã lưu Quan Hành Khiên năm {year}")
        except Exception as e:
            print(f"Lỗi khi lưu năm {year}: {e}")
    
    # Lưu prayers catalog
    prayers = db.extract_prayers_catalog()
    save_prayers_to_db(prayers)
    print(f"Đã lưu {len(prayers)} bài văn khấn")
    
    print("Hoàn thành khởi tạo database!")


if __name__ == "__main__":
    # Test: populate database from PDF
    pdf_path = Path(__file__).resolve().parents[2] / "vankhan.pdf"
    if pdf_path.exists():
        populate_database_from_pdf(pdf_path)
    else:
        print(f"Không tìm thấy file PDF: {pdf_path}")
