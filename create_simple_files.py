#!/usr/bin/env python3
"""
Script để tạo các file prayer1.html đến prayer46.html từ các file có sẵn
"""

import os
import shutil
from pathlib import Path

def create_simple_prayer_files():
    """Tạo các file prayer1.html đến prayer46.html"""
    
    # Mapping từ số thứ tự đến file thực tế
    file_mapping = {
        1: "prayerI_001.html",
        2: "prayerI_002.html", 
        3: "prayerI_003.html",
        4: "prayerI_004.html",
        5: "prayerI_005.html",
        6: "prayerII_006.html",
        7: "prayerII_007.html",
        8: "prayerII_008.html",
        9: "prayerII_009.html",
        10: "prayerII_010.html",
        11: "prayerII_011.html",
        12: "prayerII_012.html",
        13: "prayerII_013.html",
        14: "prayerII_014.html",
        15: "prayerIII_015.html",
        16: "prayerIII_016.html",
        17: "prayerIII_017.html",
        18: "prayerIII_018.html",
        19: "prayerIII_019.html",
        20: "prayerIII_020.html",
        21: "prayerIII_021.html",
        22: "prayerIV_022.html",
        23: "prayerIV_023.html",
        24: "prayerIV_024.html",
        25: "prayerIV_025.html",
        26: "prayerIV_026.html",
        27: "prayerIV_027.html",
        28: "prayerIV_028.html",
        29: "prayerIV_029.html",
        30: "prayerIV_030.html",
        31: "prayerIV_031.html",
        32: "prayerIV_032.html",
        33: "prayerIV_033.html",
        34: "prayerV_034.html",
        35: "prayerV_035.html",
        36: "prayerV_036.html",
        37: "prayerV_037.html",
        38: "prayerV_038.html",
        39: "prayerV_039.html",
        40: "prayerV_040.html",
        41: "prayerV_041.html",
        42: "prayerVI_042.html",
        43: "prayerVI_043.html",
        44: "prayerVI_044.html",
        45: "prayerVI_045.html",
        46: "prayerVI_046.html"
    }
    
    base_dir = Path("c:/Users/Admin/Desktop/app văn khấn/van-khan")
    
    for num, source_file in file_mapping.items():
        source_path = base_dir / source_file
        target_path = base_dir / f"prayer{num}.html"
        
        if source_path.exists():
            # Copy file content
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update title and header to show simple number
            content = content.replace(f"Bài Văn Khấn Số {source_file.split('_')[1].split('.')[0]}", f"Bài Văn Khấn Số {num}")
            
            # Write to target file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Đã tạo prayer{num}.html từ {source_file}")
        else:
            print(f"❌ Không tìm thấy {source_file}")
    
    print("🎉 Đã tạo xong tất cả 46 file prayer1.html đến prayer46.html!")

if __name__ == "__main__":
    create_simple_prayer_files()
