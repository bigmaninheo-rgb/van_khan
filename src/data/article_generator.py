import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class TOCItem:
    level: int  # 0 = chương chính, 1 = mục con
    number: str  # số thứ tự (I, II, 1, 2...)
    title: str
    page: int = 0  # số trang (nếu có)

class ArticleGenerator:
    def __init__(self, txt_path: Path):
        self.txt_path = txt_path
        self.toc: List[TOCItem] = []
        self.prayers: Dict[str, str] = {}
        
    def parse_toc(self) -> List[TOCItem]:
        """Phân tích mục lục từ file txt"""
        text = self.txt_path.read_text(encoding='utf-8')
        lines = text.split('\n')
        
        toc = []
        
        # Pattern cho chương chính (I, II, III...)
        chapter_pattern = re.compile(r'^(I{1,3}|IV|V|VI)\.\s*(VĂN CÚNG.+)$')
        # Pattern cho mục con (1., 2., 3...)
        item_pattern = re.compile(r'^(\d+)\.\s*(Văn cúng.+?)\s*[…\.]+\s*(\d+)$')
        
        current_chapter = ""
        
        for line in lines:
            line = line.strip()
            
            # Kiểm tra chương chính
            chap_match = chapter_pattern.match(line)
            if chap_match:
                roman = chap_match.group(1)
                title = chap_match.group(2).strip()
                toc.append(TOCItem(level=0, number=roman, title=title))
                current_chapter = roman
                continue
            
            # Kiểm tra mục con
            item_match = item_pattern.match(line)
            if item_match:
                num = item_match.group(1)
                title = item_match.group(2).strip()
                page = int(item_match.group(3))
                toc.append(TOCItem(level=1, number=num, title=title, page=page))
        
        self.toc = toc
        return toc
    
    def extract_prayer_content(self) -> Dict[str, str]:
        """Trích xuất nội dung từng bài văn cúng"""
        text = self.txt_path.read_text(encoding='utf-8')
        
        prayers = {}
        
        # Tìm từng bài theo số thứ tự
        for item in self.toc:
            if item.level == 1:  # Chỉ xử lý mục con có nội dung
                # Pattern để tìm đầu bài
                pattern = re.compile(
                    rf'{item.number}\.\s*{re.escape(item.title)}',
                    re.MULTILINE | re.IGNORECASE
                )
                
                match = pattern.search(text)
                if match:
                    start = match.start()
                    
                    # Tìm vị trí kết thúc (bài tiếp theo hoặc ===)
                    end = len(text)
                    next_idx = self.toc.index(item) + 1
                    if next_idx < len(self.toc):
                        next_item = self.toc[next_idx]
                        if next_item.level == 1:
                            next_pattern = re.compile(
                                rf'{next_item.number}\.\s*{re.escape(next_item.title)}',
                                re.MULTILINE | re.IGNORECASE
                            )
                            next_match = next_pattern.search(text)
                            if next_match:
                                end = next_match.start()
                    
                    content = text[start:end].strip()
                    prayers[item.number] = content
        
        self.prayers = prayers
        return prayers
    
    def generate_html_article(self, output_path: Path) -> None:
        """Tạo bài viết HTML với mục lục phân cấp"""
        
        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tuyển tập các bài văn cúng thông dụng trong năm</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f9f9f9;
        }
        
        h1 {
            text-align: center;
            color: #8B0000;
            font-size: 28px;
            margin-bottom: 30px;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
        }
        
        h2 {
            color: #8B0000;
            font-size: 22px;
            margin-top: 40px;
            margin-bottom: 20px;
            padding: 10px;
            background: linear-gradient(90deg, #FFF8EE, #fff);
            border-left: 5px solid #D4AF37;
        }
        
        h3 {
            color: #333;
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding: 8px 12px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        
        .toc {
            background: #fff;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }
        
        .toc h2 {
            margin-top: 0;
            text-align: center;
            border: none;
            background: none;
        }
        
        .toc-list {
            list-style: none;
        }
        
        .toc-chapter {
            font-weight: bold;
            color: #8B0000;
            margin-top: 20px;
            font-size: 16px;
        }
        
        .toc-item {
            margin-left: 20px;
            padding: 5px 0;
            border-bottom: 1px dotted #ddd;
        }
        
        .toc-item a {
            color: #333;
            text-decoration: none;
        }
        
        .toc-item a:hover {
            color: #8B0000;
        }
        
        .prayer-content {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .prayer-content p {
            margin-bottom: 15px;
            text-align: justify;
        }
        
        .prayer-content .placeholder {
            color: #8B0000;
            font-weight: bold;
            background: #FFF8EE;
            padding: 2px 8px;
            border-radius: 3px;
        }
        
        .date-info {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #8B0000;
            color: #fff;
            padding: 15px 20px;
            border-radius: 10px;
            font-size: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .date-info .label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .date-info .value {
            font-size: 16px;
            font-weight: bold;
        }
        
        @media print {
            .date-info {
                display: none;
            }
            
            body {
                background: white;
            }
            
            .prayer-content {
                box-shadow: none;
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="date-info">
        <div class="label">Ngày dương lịch:</div>
        <div class="value" id="solar-date">--/--/----</div>
        <div class="label" style="margin-top: 8px;">Ngày âm lịch:</div>
        <div class="value" id="lunar-date">--/--/----</div>
    </div>
    
    <h1>TUYỂN TẬP CÁC BÀI VĂN CÚNG THÔNG DỤNG TRONG NĂM</h1>
"""
        
        # Tạo mục lục
        html += """
    <div class="toc">
        <h2>MỤC LỤC</h2>
        <ul class="toc-list">
"""
        
        for item in self.toc:
            if item.level == 0:
                html += f'            <li class="toc-chapter">{item.number}. {item.title}</li>\n'
            else:
                anchor = f'bai-{item.number}'
                html += f'            <li class="toc-item"><a href="#{anchor}">{item.number}. {item.title}</a></li>\n'
        
        html += """        </ul>
    </div>
"""
        
        # Tạo nội dung từng bài
        current_chapter = ""
        for item in self.toc:
            if item.level == 0:
                current_chapter = item.title
                html += f'\n    <h2>{item.number}. {item.title}</h2>\n'
            else:
                anchor = f'bai-{item.number}'
                html += f'\n    <h3 id="{anchor}">{item.number}. {item.title}</h3>\n'
                
                # Thêm nội dung bài (nếu có)
                if item.number in self.prayers:
                    content = self.prayers[item.number]
                    # Format content thành HTML
                    content_html = self._format_content_to_html(content)
                    html += f'    <div class="prayer-content">\n{content_html}\n    </div>\n'
        
        # JavaScript cho ngày tháng tự động
        html += """
    <script>
        // Tự động cập nhật ngày dương lịch
        function updateSolarDate() {
            const now = new Date();
            const day = String(now.getDate()).padStart(2, '0');
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const year = now.getFullYear();
            document.getElementById('solar-date').textContent = `${day}/${month}/${year}`;
        }
        
        // Cập nhật ngày âm lịch (placeholder - cần thư viện để tính chính xác)
        function updateLunarDate() {
            // Placeholder - sẽ tích hợp thư viện âm lịch sau
            document.getElementById('lunar-date').textContent = 'Đang cập nhật...';
        }
        
        updateSolarDate();
        updateLunarDate();
    </script>
</body>
</html>
"""
        
        output_path.write_text(html, encoding='utf-8')
        print(f"✅ Đã tạo bài viết: {output_path}")
    
    def _format_content_to_html(self, content: str) -> str:
        """Chuyển nội dung văn cúng thành HTML"""
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Bỏ số thứ tự ở đầu
            line = re.sub(r'^\d+\.\s*', '', line)
            
            # Thay thế placeholder
            line = line.replace('…', '<span class="placeholder">{ten_be}</span>')
            line = line.replace('...', '<span class="placeholder">{ten_be}</span>')
            
            # Format các đoạn đặc biệt
            if line.startswith('Nam mô') or line.startswith('- Con'):
                html_lines.append(f'        <p style="margin-left: 20px;">{line}</p>')
            elif line.startswith('Hôm nay') or line.startswith('Tín chủ'):
                html_lines.append(f'        <p><strong>{line}</strong></p>')
            else:
                html_lines.append(f'        <p>{line}</p>')
        
        return '\n'.join(html_lines)
    
    def generate_markdown_article(self, output_path: Path) -> None:
        """Tạo bài viết Markdown"""
        md = """# TUYỂN TẬP CÁC BÀI VĂN CÚNG THÔNG DỤNG TRONG NĂM

> **Ngày dương lịch:** {ngay_duong_lich}  
> **Ngày âm lịch:** {ngay_am_lich}

---

## MỤC LỤC

"""
        
        for item in self.toc:
            if item.level == 0:
                md += f"\n### {item.number}. {item.title}\n\n"
            else:
                md += f"{item.number}. [{item.title}](#bai-{item.number})\n"
        
        md += "\n---\n\n"
        
        # Nội dung
        for item in self.toc:
            if item.level == 0:
                md += f"## {item.number}. {item.title}\n\n"
            else:
                md += f"### <a id='bai-{item.number}'></a>{item.number}. {item.title}\n\n"
                if item.number in self.prayers:
                    content = self.prayers[item.number]
                    md += content + "\n\n---\n\n"
        
        output_path.write_text(md, encoding='utf-8')
        print(f"✅ Đã tạo bài viết Markdown: {output_path}")


def main():
    txt_path = Path(__file__).resolve().parents[2] / "khan.txt"
    
    if not txt_path.exists():
        print(f"❌ Không tìm thấy file: {txt_path}")
        return
    
    print("=" * 60)
    print("TẠO BÀI VIẾT TỪ MỤC LỤC")
    print("=" * 60)
    
    generator = ArticleGenerator(txt_path)
    
    # Phân tích mục lục
    print("\n1. Đọc mục lục...")
    toc = generator.parse_toc()
    print(f"   Tìm thấy {len(toc)} mục")
    
    # Trích xuất nội dung
    print("\n2. Trích xuất nội dung...")
    prayers = generator.extract_prayer_content()
    print(f"   Đã trích xuất {len(prayers)} bài")
    
    # Tạo bài viết HTML
    print("\n3. Tạo bài viết HTML...")
    html_path = Path(__file__).resolve().parents[2] / "article.html"
    generator.generate_html_article(html_path)
    
    # Tạo bài viết Markdown
    print("\n4. Tạo bài viết Markdown...")
    md_path = Path(__file__).resolve().parents[2] / "article.md"
    generator.generate_markdown_article(md_path)
    
    print("\n" + "=" * 60)
    print("HOÀN THÀNH!")
    print("=" * 60)
    print(f"\n📄 HTML: {html_path}")
    print(f"📝 Markdown: {md_path}")
    print("\nCác file sẵn sàng để đăng lên blog/website!")


if __name__ == "__main__":
    main()
