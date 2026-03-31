#!/usr/bin/env python3
"""
Script đơn giản để copy 46 bài văn khấn từ database và tạo trang web
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

def create_prayers_html(prayers):
    """Tạo trang prayers.html với 46 bài"""
    
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
        
        .prayer-list {
            display: grid;
            gap: 15px;
        }
        
        .prayer-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #8B0000;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        
        .prayer-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .prayer-title {
            font-size: 18px;
            font-weight: bold;
            color: #8B0000;
            margin-bottom: 8px;
        }
        
        .prayer-description {
            font-size: 14px;
            color: #666;
            line-height: 1.5;
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
            
            .prayer-card {
                padding: 15px;
            }
            
            .prayer-title {
                font-size: 16px;
            }
            
            .prayer-description {
                font-size: 13px;
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
            <div class="prayer-list">
'''
    
    # Thêm 46 bài vào HTML
    for i, prayer in enumerate(prayers, 1):
        html_content += f'''
                <div class="prayer-card" onclick="openPrayer({i}, 'prayer{i}.html')">
                    <div class="prayer-title">{prayer['title']}</div>
                    <div class="prayer-description">{prayer['description']}</div>
                </div>
'''
    
    html_content += '''
            </div>
        </div>
        
        <div class="install-section">
            <p style="margin-bottom: 15px; color: #666;">📱 Cài đặt ứng dụng để dùng mọi lúc mọi nơi</p>
            <button class="install-btn" onclick="installPWA()">
                📱 Cài đặt ứng dụng
            </button>
        </div>
    </div>
    
    <script>
        function openPrayer(id, url) {{
            // Mở trang chi tiết bài văn khấn
            window.location.href = url;
        }}
        
        // PWA Install
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
        }});
        
        function installPWA() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted A2HS prompt');
                    }} else {{
                        console.log('User dismissed A2HS prompt');
                    }}
                    deferredPrompt = null;
                }});
            }} else {{
                // Fallback cho iOS
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {{
                    alert('Để cài đặt: 1. Nhấn Share 2. Chọn "Add to Home Screen"');
                }} else {{
                    alert('Ứng dụng đã được tối ưu cho cài đặt PWA');
                }}
            }}
        }}
        
        // Service Worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('/sw.js');
        }}
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main function"""
    print("Đang extract 46 bài văn khấn từ database...")
    
    # Extract prayers
    prayers = extract_prayers_from_db()
    
    if not prayers:
        print("Không extract được bài văn khấn nào!")
        return
    
    # Tạo HTML
    html_content = create_prayers_html(prayers)
    
    # Lưu vào file prayers.html
    output_path = Path("c:/Users/Admin/Desktop/app văn khấn/van-khan/prayers.html")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Đã tạo trang prayers.html với {len(prayers)} bài văn khấn!")
    print(f"File được lưu tại: {output_path}")
    
    # Tạo các trang chi tiết
    for prayer in prayers:
        create_prayer_detail_page(prayer)
    
    print("Đã tạo tất cả 46 trang chi tiết!")

def create_prayer_detail_page(prayer):
    """Tạo trang chi tiết cho từng bài"""
    
    # Xử lý template để loại bỏ escape characters
    template = prayer['template'].replace('\\"', '"').replace('\\n', '\n')
    
    html_content = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bài Văn Khấn Số {prayer['id']} - Văn Khấn Cổ Truyền</title>
    <meta name="description" content="{prayer['description']}">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/png" sizes="32x32" href="icons/icon-192.png">
    <link rel="apple-touch-icon" sizes="192x192" href="icons/apple-touch-icon-192.png">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #8B0000 0%, #FF6B6B 100%);
            color: #333;
            min-height: 100vh;
            padding: 10px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: #8B0000;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        .back-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            transition: background 0.3s;
        }}
        
        .back-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .content {{
            padding: 20px;
            max-height: calc(100vh - 140px);
            overflow-y: auto;
        }}
        
        .prayer-content {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 30px;
            border-left: 4px solid #8B0000;
            line-height: 1.8;
            font-size: 16px;
        }}
        
        .prayer-title {{
            font-size: 20px;
            font-weight: bold;
            color: #8B0000;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .prayer-text {{
            white-space: pre-wrap;
            color: #333;
            margin-bottom: 20px;
        }}
        
        .personalization-form {{
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .form-group {{
            margin-bottom: 15px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #8B0000;
        }}
        
        .form-group input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            min-height: 100px;
            resize: vertical;
        }}
        
        .btn {{
            background: #8B0000;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 5px;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #6B0000;
        }}
        
        .btn-secondary {{
            background: #6c757d;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
        }}
        
        .install-section {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 5px;
            }}
            
            .container {{
                margin: 0;
                border-radius: 0;
                box-shadow: none;
            }}
            
            .header {{
                padding: 10px 15px;
            }}
            
            .header h1 {{
                font-size: 16px;
            }}
            
            .content {{
                padding: 15px;
                max-height: calc(100vh - 120px);
            }}
            
            .prayer-content {{
                padding: 20px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bài Văn Khấn Số {prayer['id']}</h1>
            <a href="prayers.html" class="back-btn">← Quay lại danh mục</a>
        </div>
        
        <div class="content">
            <div class="prayer-content">
                <div class="prayer-title">{prayer['title']}</div>
                
                <div class="prayer-text">
{template}
                </div>
                
                <div class="personalization-form">
                    <h3>📝 Tùy chỉnh thông tin cá nhân</h3>
                    
                    <div class="form-group">
                        <label for="ten_be">Tên bé / Tên gia chủ:</label>
                        <input type="text" id="ten_be" placeholder="Nhập tên bé hoặc tên gia chủ">
                    </div>
                    
                    <div class="form-group">
                        <label for="dia_chi">Địa chỉ:</label>
                        <input type="text" id="dia_chi" placeholder="Nhập địa chỉ nhà">
                    </div>
                    
                    <div class="form-group">
                        <label for="ngay_thang">Ngày tháng dương lịch:</label>
                        <input type="text" id="ngay_thang" placeholder="ngày 25/12/2025">
                    </div>
                    
                    <div class="form-group">
                        <label for="ngay_am_lich">Ngày tháng âm lịch:</label>
                        <input type="text" id="ngay_am_lich" placeholder="ngày 01/11/Ất Dần">
                    </div>
                    
                    <div class="form-group">
                        <label for="nam">Năm:</label>
                        <input type="number" id="nam" placeholder="2025">
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <button class="btn" onclick="personalizePrayer()">📝 Cá nhân hóa bài văn</button>
                        <button class="btn btn-secondary" onclick="copyPrayer()">📋 Sao chép bài văn</button>
                        <button class="btn btn-secondary" onclick="sharePrayer()">🔗 Chia sẻ bài văn</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="install-section">
            <p style="margin-bottom: 15px; color: #666;">📱 Cài đặt ứng dụng để lưu thông tin và dùng mọi lúc mọi nơi</p>
            <button class="btn" onclick="installPWA()">
                📱 Cài đặt ứng dụng
            </button>
        </div>
    </div>
    
    <script>
        function personalizePrayer() {{
            const tenBe = document.getElementById('ten_be').value;
            const diaChi = document.getElementById('dia_chi').value;
            const ngayThang = document.getElementById('ngay_thang').value;
            const ngayAmLich = document.getElementById('ngay_am_lich').value;
            const nam = document.getElementById('nam').value;
            
            if (!tenBe) {{
                alert('Vui lòng nhập tên bé hoặc tên gia chủ');
                return;
            }}
            
            // Thay thế placeholder trong bài văn
            let prayerText = document.querySelector('.prayer-text').textContent;
            prayerText = prayerText.replace(/\\[Tên bé\/Tên gia chủ\\]/g, tenBe);
            prayerText = prayerText.replace(/\\[Địa chỉ\\]/g, diaChi);
            prayerText = prayerText.replace(/\\[Ngày tháng dương lịch\\]/g, ngayThang);
            prayerText = prayerText.replace(/\\[Ngày tháng âm lịch\\]/g, ngayAmLich);
            prayerText = prayerText.replace(/\\[Năm\\]/g, nam);
            
            // Cập nhật nội dung
            document.querySelector('.prayer-text').textContent = prayerText;
            
            // Lưu vào localStorage
            localStorage.setItem('van_khan_settings', JSON.stringify({{
                ten_be: tenBe,
                dia_chi: diaChi,
                ngay_thang: ngayThang,
                ngay_am_lich: ngayAmLich,
                nam: nam
            }}));
            
            alert('Đã cá nhân hóa bài văn khấn! Thông tin đã được lưu.');
        }}
        
        function copyPrayer() {{
            const prayerText = document.querySelector('.prayer-text').textContent;
            navigator.clipboard.writeText(prayerText);
            alert('Đã sao chép bài văn khấn!');
        }}
        
        function sharePrayer() {{
            const prayerText = document.querySelector('.prayer-text').textContent;
            
            if (navigator.share) {{
                navigator.share({{
                    title: 'Bài Văn Khấn',
                    text: prayerText
                }});
            }} else {{
                // Fallback cho browsers không hỗ trợ Web Share API
                const textArea = document.createElement('textarea');
                textArea.value = prayerText;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Đã sao chép bài văn khấn! Bạn có thể dán vào nơi khác.');
            }}
        }}
        
        // Load settings từ localStorage
        window.addEventListener('DOMContentLoaded', function() {{
            const settings = localStorage.getItem('van_khan_settings');
            if (settings) {{
                const parsed = JSON.parse(settings);
                document.getElementById('ten_be').value = parsed.ten_be || '';
                document.getElementById('dia_chi').value = parsed.dia_chi || '';
                document.getElementById('ngay_thang').value = parsed.ngay_thang || '';
                document.getElementById('ngay_am_lich').value = parsed.ngay_am_lich || '';
                document.getElementById('nam').value = parsed.nam || '';
                
                // Cá nhân hóa bài văn
                if (parsed.ten_be) {{
                    personalizePrayer();
                }}
            }}
        }});
        
        // PWA Install
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
        }});
        
        function installPWA() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted A2HS prompt');
                    }} else {{
                        console.log('User dismissed A2HS prompt');
                    }}
                    deferredPrompt = null;
                }});
            }} else {{
                // Fallback cho iOS
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {{
                    alert('Để cài đặt: 1. Nhấn Share 2. Chọn "Add to Home Screen"');
                }} else {{
                    alert('Ứng dụng đã được tối ưu cho cài đặt PWA');
                }}
            }}
        }}
        
        // Service Worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('/sw.js');
        }}
    </script>
</body>
</html>'''
    
    # Lưu trang chi tiết
    output_path = Path(f"c:/Users/Admin/Desktop/app văn khấn/van-khan/prayer{prayer['id']}.html")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Đã tạo trang prayer{prayer['id']}.html")

if __name__ == "__main__":
    main()
