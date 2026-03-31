#!/usr/bin/env python3
"""
Script để tạo prayers.html theo nhóm như trong main.py
"""

import sqlite3
import json
from pathlib import Path

def extract_prayers_from_db():
    """Extract 46 bài văn khấn từ database"""
    
    db_path = Path("c:/Users/Admin/Desktop/app văn khấn/data/vankhan.db")
    
    if not db_path.exists():
        print("Không tìm thấy database vankhan.db")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lấy tất cả prayers từ database
        cursor.execute("SELECT id, title, template FROM prayers ORDER BY id")
        rows = cursor.fetchall()
        
        prayers = []
        for row in rows:
            prayers.append({
                'id': row[0],
                'title': row[1],
                'description': row[1],  # Dùng title làm description
                'template': row[2]
            })
        
        conn.close()
        print(f"Đã extract {len(prayers)} bài văn khấn từ database")
        return prayers
        
    except Exception as e:
        print(f"Lỗi khi đọc database: {e}")
        return []

def create_grouped_prayers_html(prayers):
    """Tạo trang prayers.html theo nhóm như trong main.py"""
    
    # Sắp xếp theo ID
    ordered_catalog = sorted(prayers, key=lambda x: x['id'])
    
    # Tạo các nhóm đúng theo mục lục từ khan.txt
    catalog_groups = {
        "I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG": [],
        "II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN": [],
        "III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN": [],
        "IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC": [],
        "V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU": [],
        "VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG": []
    }
    
    # Phân loại các bài vào nhóm
    for item in ordered_catalog:
        item_id = item.get("id", "")
        if item_id.startswith('I_'):
            catalog_groups["I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG"].append(item)
        elif item_id.startswith('II_'):
            catalog_groups["II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN"].append(item)
        elif item_id.startswith('III_'):
            catalog_groups["III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN"].append(item)
        elif item_id.startswith('IV_'):
            catalog_groups["IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC"].append(item)
        elif item_id.startswith('V_'):
            catalog_groups["V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU"].append(item)
        elif item_id.startswith('VI_'):
            catalog_groups["VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG"].append(item)
    
    # Sắp xếp lại từng nhóm theo đúng thứ tự ID
    for group_name in catalog_groups:
        catalog_groups[group_name].sort(key=lambda x: x['id'])
    
    html_content = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>46 Bài Văn Khấn - Văn Khấn Cổ Truyền</title>
    <meta name="description" content="46 bài văn khấn đầy đủ cho các dịp lễ tết, cúng giỗ, thọ, cưới hỏi">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/png" sizes="32x32" href="icons/icon-192.png">
    <link rel="apple-touch-icon" sizes="192x192" href="icons/apple-touch-icon-192.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #8B0000 0%, #FF6B6B 100%);
            color: #333;
            min-height: 100vh;
            padding: 10px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: #8B0000;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 20px;
            font-weight: bold;
        }
        
        .back-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .content {
            padding: 20px;
            max-height: calc(100vh - 140px);
            overflow-y: auto;
        }
        
        .group-section {
            margin-bottom: 25px;
        }
        
        .group-title {
            background: #8B0000;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .prayer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .prayer-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #8B0000;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        
        .prayer-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .prayer-number {
            display: inline-block;
            background: #8B0000;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .prayer-title {
            font-size: 14px;
            font-weight: bold;
            color: #8B0000;
            margin-bottom: 5px;
            line-height: 1.3;
        }
        
        .prayer-description {
            font-size: 12px;
            color: #666;
            line-height: 1.4;
        }
        
        .install-section {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #eee;
        }
        
        .install-btn {
            background: #8B0000;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
            transition: background 0.3s;
        }
        
        .install-btn:hover {
            background: #6B0000;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 5px;
            }
            
            .container {
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }
            
            .header {
                padding: 10px 15px;
            }
            
            .header h1 {
                font-size: 16px;
            }
            
            .content {
                padding: 15px;
                max-height: calc(100vh - 120px);
            }
            
            .group-title {
                font-size: 14px;
                padding: 10px 15px;
            }
            
            .prayer-grid {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            
            .prayer-card {
                padding: 12px;
            }
            
            .prayer-title {
                font-size: 13px;
            }
            
            .prayer-description {
                font-size: 11px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>46 Bài Văn Khấn</h1>
            <a href="/" class="back-btn">← Trang chủ</a>
        </div>
        
        <div class="content">
'''
    
    # Thêm các nhóm vào HTML
    for group_name, items in catalog_groups.items():
        if items:  # Chỉ hiển thị nhóm có bài
            html_content += f'''
            <div class="group-section">
                <div class="group-title">{group_name}</div>
                <div class="prayer-grid">
'''
            
            # Thêm các bài trong nhóm
            for item in items:
                # Lấy số thứ tự từ ID (ví dụ: I_001 -> 1)
                prayer_num = item['id'].split('_')[1].lstrip('0')
                if prayer_num == '':
                    prayer_num = '1'
                
                html_content += f'''
                    <div class="prayer-card" onclick="openPrayer('{prayer_num}', 'prayer{prayer_num}.html')">
                        <div class="prayer-number">Bài {prayer_num}</div>
                        <div class="prayer-title">{item['title']}</div>
                        <div class="prayer-description">{item['description']}</div>
                    </div>
'''
            
            html_content += '''
                </div>
            </div>
'''
    
    html_content += '''
        </div>
        
        <div class="install-section">
            <p style="margin-bottom: 15px; color: #666;">📱 Cài đặt ứng dụng để dùng mọi lúc mọi nơi</p>
            <button class="install-btn" onclick="installPWA()">
                📱 Cài đặt ứng dụng
            </button>
        </div>
    </div>
    
    <script>
        function openPrayer(id, url) {
            // Mở trang chi tiết bài văn khấn
            window.location.href = url;
        }
        
        // PWA Install
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
        });
        
        function installPWA() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted A2HS prompt');
                    } else {
                        console.log('User dismissed A2HS prompt');
                    }
                    deferredPrompt = null;
                });
            } else {
                // Fallback cho iOS
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                    alert('Để cài đặt: 1. Nhấn Share 2. Chọn "Add to Home Screen"');
                } else {
                    alert('Ứng dụng đã được tối ưu cho cài đặt PWA');
                }
            }
        }
        
        // Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main function"""
    print("Đang tạo prayers.html theo nhóm như trong main.py...")
    
    # Extract prayers
    prayers = extract_prayers_from_db()
    
    if not prayers:
        print("Không extract được bài văn khấn nào!")
        return
    
    # Tạo HTML theo nhóm
    html_content = create_grouped_prayers_html(prayers)
    
    # Lưu vào file prayers.html
    output_path = Path("c:/Users/Admin/Desktop/app văn khấn/van-khan/prayers.html")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Đã tạo trang prayers.html theo nhóm với {len(prayers)} bài văn khấn!")
    print(f"File được lưu tại: {output_path}")
    
    # Hiển thị thống kê
    print("\n📊 Thống kê nhóm:")
    ordered_catalog = sorted(prayers, key=lambda x: x['id'])
    
    catalog_groups = {
        "I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG": [],
        "II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN": [],
        "III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN": [],
        "IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC": [],
        "V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU": [],
        "VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG": []
    }
    
    for item in ordered_catalog:
        item_id = item.get("id", "")
        if item_id.startswith('I_'):
            catalog_groups["I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG"].append(item)
        elif item_id.startswith('II_'):
            catalog_groups["II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN"].append(item)
        elif item_id.startswith('III_'):
            catalog_groups["III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN"].append(item)
        elif item_id.startswith('IV_'):
            catalog_groups["IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC"].append(item)
        elif item_id.startswith('V_'):
            catalog_groups["V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU"].append(item)
        elif item_id.startswith('VI_'):
            catalog_groups["VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG"].append(item)
    
    for group_name, items in catalog_groups.items():
        if items:
            print(f"  {group_name}: {len(items)} bài")

if __name__ == "__main__":
    main()
