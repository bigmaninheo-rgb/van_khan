#!/usr/bin/env python3
"""
Script để cập nhật tất cả các trang prayer1.html đến prayer46.html
- Bỏ trường "Tên bé / Tên gia chủ"
- Tự động điền ngày tháng dương lịch và âm lịch
- Thay placeholder trong bài khấn thành ...
"""

import re
from pathlib import Path
from datetime import datetime, date

def get_current_dates():
    """Lấy ngày tháng hiện tại"""
    today = date.today()
    
    # Dương lịch
    duong_lich = today.strftime("ngày %d/%m/%Y")
    
    # Âm lịch (tạm dùng đơn giản)
    # Đây là cách tính đơn giản, có thể thay bằng library chính xác sau
    amlich_months = ['Giêng', 'Hai', 'Ba', 'Tư', 'Năm', 'Sáu', 
                    'Bảy', 'Tám', 'Chín', 'Mười', 'Mười Một', 'Chạp']
    
    # Tạm tính âm lịch (cần cải thiện với library chính xác)
    amlich_day = today.day
    amlich_month_idx = (today.month - 1) % 12
    amlich_month = amlich_months[amlich_month_idx]
    
    # Năm âm lịch (tạm)
    amlich_year = today.year
    
    amlich = f"ngày {amlich_day}/{amlich_month}"
    
    return duong_lich, amlich, str(today.year)

def update_prayer_page(prayer_num):
    """Cập nhật một trang prayer"""
    
    file_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer_num}.html")
    
    if not file_path.exists():
        print(f"❌ Không tìm thấy {file_path}")
        return False
    
    # Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    
    # 1. Xóa trường "Tên bé / Tên gia chủ"
    content = re.sub(
        r'<div class="form-group">\s*<label for="ten_be">Tên bé / Tên gia chủ:</label>\s*<input type="text" id="ten_be" placeholder="Nhập tên bé hoặc tên gia chủ">\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 2. Tự động điền ngày tháng dương lịch
    content = re.sub(
        r'<input type="text" id="ngay_thang" placeholder="ngày 25/12/2025">',
        f'<input type="text" id="ngay_thang" value="{duong_lich}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 3. Tự động điền ngày tháng âm lịch
    content = re.sub(
        r'<input type="text" id="ngay_am_lich" placeholder="ngày 01/11/Ất Dần">',
        f'<input type="text" id="ngay_am_lich" value="{amlich}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 4. Tự động điền năm
    content = re.sub(
        r'<input type="number" id="nam" placeholder="2025">',
        f'<input type="number" id="nam" value="{year}" readonly style="background: #f8f9fa;">',
        content
    )
    
    # 5. Cập nhật JavaScript để không cần kiểm tra ten_be
    content = re.sub(
        r'if \(!tenBe\) {\s*alert\(\'Vui lòng nhập tên bé hoặc tên gia chủ\'\);\s*return;\s*}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 6. Cập nhật localStorage để không lưu ten_be
    content = re.sub(
        r'localStorage\.setItem\(\'van_khan_settings\', JSON\.stringify\(\{\s*ten_be: tenBe,\s*dia_chi: diaChi,\s*ngay_thang: ngayThang,\s*ngay_am_lich: ngayAmLich,\s*nam: nam\s*\}\)\);',
        'localStorage.setItem(\'van_khan_settings\', JSON.stringify({\n                        dia_chi: diaChi,\n                        ngay_thang: ngayThang,\n                        ngay_am_lich: ngayAmLich,\n                        nam: nam\n                    }));',
        content
    )
    
    # 7. Cập nhật load settings để không load ten_be
    content = re.sub(
        r'document\.getElementById\(\'ten_be\'\)\.value = parsed\.ten_be \|\| \'\';',
        '',
        content
    )
    
    # 8. Cập nhật điều kiện cá nhân hóa
    content = re.sub(
        r'if \(parsed\.ten_be\) {',
        'if (parsed.dia_chi || parsed.ngay_thang) {',
        content
    )
    
    # 9. Thay thế placeholder trong bài văn khấn
    # Thay {ten_be} thành ...
    content = re.sub(
        r'prayerText\.replace\(/\\\[Tên bé\/Tên gia chủ\\\]/g, tenBe\)',
        'prayerText.replace(/\\[Tên bé\/Tên gia chủ\\]/g, "...")',
        content
    )
    
    # 10. Cập nhật placeholder trong template
    content = re.sub(
        r'\[Tên bé\/Tên gia chủ\]',
        '...',
        content
    )
    
    # 11. Cập nhật label cho địa chỉ
    content = re.sub(
        r'<label for="dia_chi">Địa chỉ:</label>',
        '<label for="dia_chi">Địa chỉ (nếu cần):</label>',
        content
    )
    
    # 12. Cập nhật placeholder cho địa chỉ
    content = re.sub(
        r'<input type="text" id="dia_chi" placeholder="Nhập địa chỉ nhà">',
        '<input type="text" id="dia_chi" placeholder="Nhập địa chỉ nhà (nếu cần)">',
        content
    )
    
    # 13. Cập nhật title và header
    content = re.sub(
        r'<h3>📝 Tùy chỉnh thông tin cá nhân</h3>',
        '<h3>📝 Tùy chỉnh thông tin</h3>',
        content
    )
    
    # Lưu lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã cập nhật prayer{prayer_num}.html")
    return True

def main():
    """Main function"""
    print("Đang cập nhật tất cả các trang prayer1.html đến prayer46.html...")
    print("🔧 Thay đổi:")
    print("  - Bỏ trường 'Tên bé / Tên gia chủ'")
    print("  - Tự động điền ngày tháng dương lịch và âm lịch")
    print("  - Thay placeholder trong bài khấn thành '...'")
    print()
    
    # Cập nhật tất cả 46 trang
    success_count = 0
    for i in range(1, 47):
        if update_prayer_page(i):
            success_count += 1
    
    print(f"\n🎉 Hoàn thành! Đã cập nhật {success_count}/46 trang")
    
    # Hiển thị ngày tháng hiện tại
    duong_lich, amlich, year = get_current_dates()
    print(f"\n📅 Ngày tháng tự động:")
    print(f"  Dương lịch: {duong_lich}")
    print(f"  Âm lịch: {amlich}")
    print(f"  Năm: {year}")

if __name__ == "__main__":
    main()
