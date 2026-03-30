from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import flet as ft

from core.config import load_config, save_config
from core.logic import build_lunar_date_text, personalize_prayer
# Không còn dùng PDF nữa - dữ liệu từ khan.txt
from data.sqlite_db import get_prayers_from_db


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "seed_data.json"
PRAYERS_PATH = ROOT / "data" / "prayers.json"

# Không còn dùng PDF nữa - dữ liệu từ khan.txt
# PDF_SOURCE = ROOT / "vankhan1.pdf"

COLOR_BG = "#FFF8EE"
COLOR_PRIMARY = "#8B0000"
COLOR_ACCENT = "#D4AF37"


def ensure_seed_data() -> Dict[str, Any]:
    """Trả về dữ liệu mẫu từ khan.txt thay vì PDF"""
    # Nếu chưa có seed data, tạo từ khan.txt
    if not SEED_PATH.exists():
        from data.khan_parser import parse_khan_txt
        prayers = parse_khan_txt()
        seed_data = {
            "prayers": {p['id']: p['template'] for p in prayers},
            "titles": {p['id']: p['title'] for p in prayers}
        }
        SEED_PATH.write_text(json.dumps(seed_data, ensure_ascii=False, indent=2), encoding='utf-8')
    return json.loads(SEED_PATH.read_text(encoding='utf-8'))


def load_catalog(seed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Thử đọc từ SQLite database trước
    try:
        catalog = get_prayers_from_db()
        if catalog:
            print(f"Đã tải {len(catalog)} bài từ SQLite database")
            return catalog
    except Exception as e:
        print(f"Lỗi đọc từ database: {e}")
    
    # Fallback sang file JSON nếu database không có
    if not PRAYERS_PATH.exists():
        return []
    
    try:
        with open(PRAYERS_PATH, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception:
        return []
        
    items = raw.get("Danh mục", [])
    for item in items:
        if item.get("template_key"):
            item["template"] = seed_data.get(item["template_key"], item.get("template", ""))
    return items


def main(page: ft.Page) -> None:
    page.title = "Văn khấn cổ truyền"
    page.bgcolor = COLOR_BG
    page.padding = 16
    page.theme = ft.Theme(color_scheme_seed=COLOR_PRIMARY)
    page.scroll = ft.ScrollMode.AUTO

    try:
        seed_data = ensure_seed_data()
        catalog = load_catalog(seed_data)
        config = load_config(ROOT / "config.json")
    except Exception as exc:
        page.add(
            ft.Text("Không thể khởi tạo dữ liệu ứng dụng.", size=24, color=COLOR_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(str(exc), color="#AA0000"),
        )
        page.update()
        raise

    ten_be = ft.TextField(label="Tên bé / Tên gia chủ", value=config["ten_be"])
    dia_chi = ft.TextField(label="Địa chỉ", value=config["dia_chi"])
    ngay_thang = ft.TextField(
        label="Ngày tháng hiển thị",
        value=config["ngay_thang"] or datetime.now().strftime("ngày %d/%m/%Y"),
    )
    ngay_am_lich = ft.TextField(
        label="Ngày âm lịch hiển thị",
        value=config["ngay_am_lich"] or build_lunar_date_text(),
    )
    year_field = ft.TextField(label="Năm dương lịch", value=str(config["year"]))
    
    # Auto-update ngày tháng khi khởi động
    if not config["ngay_thang"]:
        ngay_thang.value = datetime.now().strftime("ngày %d/%m/%Y")
    if not config["ngay_am_lich"]:
        ngay_am_lich.value = build_lunar_date_text()
    if not config["year"]:
        year_field.value = str(datetime.now().year)

    state: Dict[str, Any] = {"font_size": 22, "content": "", "title": "", "screen": "home", "search": "", "current_item": None}

    reader_text = ft.Text(value="", size=state["font_size"], color=COLOR_PRIMARY, selectable=True)
    snack = ft.SnackBar(content=ft.Text(""))
    search_field = ft.TextField(
        label="Tìm bài văn khấn",
        hint_text="Nhập từ khóa: giao thừa, đầy tháng, thần tài...",
        prefix_icon=ft.Icons.SEARCH,
    )
    
    # Cache cho ngày âm lịch để không tính lại nhiều lần
    _lunar_date_cache = {}

    def show_message(msg: str) -> None:
        snack.content = ft.Text(msg)
        page.snack_bar = snack
        snack.open = True
        page.update()

    def on_save_config(_: ft.ControlEvent) -> None:
        try:
            year_value = int(year_field.value.strip())
        except ValueError:
            show_message("Năm không hợp lệ. Vui lòng nhập số.")
            return
        save_config(
            {
                "ten_be": ten_be.value.strip(),
                "dia_chi": dia_chi.value.strip() or "Quế Võ, Bắc Ninh",
                "ngay_thang": ngay_thang.value.strip(),
                "ngay_am_lich": ngay_am_lich.value.strip(),
                "year": year_value,
            },
            ROOT / "config.json",
        )
        show_message("Đã lưu thông tin vào config.json")

    def build_top_bar() -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Văn khấn cổ truyền", size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                ft.PopupMenuButton(
                    icon=ft.Icons.MENU,
                    items=[
                        ft.PopupMenuItem(content="Trang chủ", on_click=lambda e: navigate("home")),
                        ft.PopupMenuItem(content="Danh mục", on_click=lambda e: navigate("catalog")),
                        ft.PopupMenuItem(content="Cài đặt", on_click=lambda e: navigate("settings")),
                    ],
                ),
            ],
        )

    def render_home() -> List[ft.Control]:
        # Sắp xếp catalog theo đúng thứ tự mục lục
        ordered_catalog = sorted(catalog, key=lambda x: x['id'])
        
        # Tạo các nhóm đúng theo mục lục từ khan.txt
        catalog_groups = {
            "I. VĂN CÚNG LỄ MỪNG THỌ, CƯỚI HỎI, SINH DƯỠNG": [],
            "II. VĂN CÚNG LỄ TANG, GIỖ TỔ TIÊN": [],
            "III. VĂN CÚNG DỊP TẾT NGUYÊN ĐÁN": [],
            "IV. VĂN CÚNG NGÀY RẰM, MỒNG 1 VÀ CÁC NGÀY LỄ TẾT KHÁC": [],
            "V. VĂN CÚNG KHI ĐI LỄ CHÙA, ĐÌNH, MIẾU": [],
            "VI. VĂN CÚNG DỊP LÀM NHÀ, CHUYỂN NHÀ, TÂN GIA, KHAI TRƯƠNG": []
        }
        
        # Phân loại các bài vào nhóm theo đúng ID (I_, II_, III_, IV_, V_, VI_)
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
        
        # Tạo các card cho mỗi nhóm
        group_cards = []
        for group_name, items in catalog_groups.items():
            if items:  # Chỉ hiển thị nhóm có bài
                # Tạo các button cho từng bài trong nhóm
                prayer_buttons = []
                for item in items:  # Hiển thị tất cả các bài
                    # Tạo handler riêng để tránh closure issue
                    def make_handler(prayer):
                        def handler(e):
                            open_reader(prayer)
                        return handler
                    
                    prayer_buttons.append(
                        ft.Button(
                            content=ft.Text(item["title"], color=ft.Colors.WHITE, size=10),
                            on_click=make_handler(item),
                            style=ft.ButtonStyle(
                                bgcolor=COLOR_PRIMARY,
                                padding=10,
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        )
                    )
                
                # Xác định chiều cao container dựa trên số bài và kích thước màn hình
                container_height = min(400, max(150, len(items) * 30))
                
                group_cards.append(
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        border=ft.Border.all(2, COLOR_ACCENT),
                        border_radius=10,
                        padding=15,
                        content=ft.Column([
                            ft.Text(group_name, size=14, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                            ft.Container(
                                height=container_height,
                                content=ft.Column(
                                    prayer_buttons, 
                                    spacing=3,
                                    scroll=ft.ScrollMode.AUTO
                                )
                            )
                        ])
                    )
                )
        
        return [
            build_top_bar(),
            ft.Text("Văn Khấn Cúng Bái - Mục Lục Gốc", size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ft.Text(
                "Chọn bài văn khấn theo mục lục gốc. Thông tin cá nhân được quản lý ở mục Cài đặt.",
                size=14,
            ),
            ft.Row(
                controls=[
                    ft.OutlinedButton("Quản lý mục lục", on_click=lambda e: navigate("editor")),
                    ft.OutlinedButton("Mở cài đặt", on_click=lambda e: navigate("settings")),
                ]
            ),
            ft.Container(
                height=600,
                content=ft.Column(
                    group_cards, 
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO
                ),
                expand=True
            )
        ]

    def render_settings() -> List[ft.Control]:
        return [
            build_top_bar(),
            ft.Text("Cài đặt thông tin cá nhân", size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            ten_be,
            dia_chi,
            ngay_thang,
            ngay_am_lich,
            year_field,
            ft.Row(
                controls=[
                    ft.Button("Lưu thông tin", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_save_config),
                    ft.OutlinedButton(
                        "Cập nhật hôm nay",
                        on_click=lambda e: update_today(),
                    ),
                    ft.OutlinedButton("Về trang chủ", on_click=lambda e: navigate("home")),
                ]
            ),
        ]

    def render_catalog() -> List[ft.Control]:
        cards: List[ft.Control] = []
        keyword = state["search"].strip().lower()
        filtered_catalog = []
        for item in catalog:
            title = (item.get("title") or "").lower()
            template = (item.get("template") or "").lower()
            if not keyword or keyword in title or keyword in template:
                filtered_catalog.append(item)

        for item in filtered_catalog:
            # Tạo handler riêng để tránh closure issue
            def make_catalog_handler(prayer):
                def handler(e):
                    open_reader(prayer)
                return handler
            
            cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.ListTile(
                            title=ft.Text(item["title"], color=COLOR_PRIMARY, size=20),
                            subtitle=ft.Text("Nhấn để mở chế độ đọc"),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=COLOR_ACCENT),
                            on_click=make_catalog_handler(item),
                        ),
                    )
                )
            )
        return [
            build_top_bar(),
            ft.Row(
                controls=[
                    ft.Text("Danh mục bài cúng", size=30, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                    ft.OutlinedButton("Về trang chủ", on_click=lambda e: navigate("home")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            search_field,
            ft.Text(f"Tìm thấy {len(filtered_catalog)} bài", color=COLOR_PRIMARY),
            *cards,
        ]

    def render_editor() -> List[ft.Control]:
        """Màn hình quản lý mục lục - Thêm/Sửa/Xóa bài khấn"""
        prayers_list = get_prayers_from_db()
        
        # Các trường nhập liệu cho bài mới
        new_title = ft.TextField(label="Tên bài văn khấn", width=400)
        new_content = ft.TextField(label="Nội dung bài khấn", multiline=True, min_lines=5, max_lines=10, width=400)
        new_chapter = ft.Dropdown(
            label="Chương mục",
            width=200,
            options=[
                ft.dropdown.Option("I", "I. Mừng thọ, Cưới hỏi, Sinh dưỡng"),
                ft.dropdown.Option("II", "II. Tang, Giỗ tổ tiên"),
                ft.dropdown.Option("III", "III. Tết Nguyên Đán"),
                ft.dropdown.Option("IV", "IV. Rằm, Mồng 1 và các ngày lễ khác"),
                ft.dropdown.Option("V", "V. Lễ chùa, Đình, Miếu"),
                ft.dropdown.Option("VI", "VI. Làm nhà, Chuyển nhà, Tân gia, Khai trương"),
            ],
            value="I"
        )
        
        message_text = ft.Text(color=COLOR_PRIMARY)
        
        def on_add_new(e):
            if not new_title.value.strip():
                message_text.value = "Vui lòng nhập tên bài!"
                page.update()
                return
            
            # Tạo ID mới
            existing_ids = [p['id'] for p in prayers_list if p['id'].startswith(f"{new_chapter.value}_")]
            max_num = 0
            for id_str in existing_ids:
                try:
                    num = int(id_str.split('_')[1])
                    max_num = max(max_num, num)
                except:
                    pass
            new_id = f"{new_chapter.value}_{max_num + 1:03d}"
            
            # Thêm vào database
            from data.sqlite_db import save_prayers_to_db
            new_prayer = {
                'id': new_id,
                'title': new_title.value.strip(),
                'template': new_content.value.strip()
            }
            save_prayers_to_db([new_prayer])
            
            message_text.value = f"✅ Đã thêm bài: {new_title.value} (ID: {new_id})"
            new_title.value = ""
            new_content.value = ""
            page.update()
        
        # Danh sách bài hiện có để xóa
        delete_dropdown = ft.Dropdown(
            label="Chọn bài để xóa",
            width=400,
            options=[ft.dropdown.Option(p['id'], f"{p['id']} - {p['title'][:40]}") for p in prayers_list]
        )
        
        def on_delete(e):
            if not delete_dropdown.value:
                message_text.value = "Vui lòng chọn bài để xóa!"
                page.update()
                return
            
            # Xóa khỏi database
            import sqlite3
            db_path = ROOT / "data" / "vankhan.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prayers WHERE id = ?", (delete_dropdown.value,))
            conn.commit()
            conn.close()
            
            message_text.value = f"✅ Đã xóa bài: {delete_dropdown.value}"
            page.update()
        
        return [
            build_top_bar(),
            ft.Text("Quản lý mục lục bài khấn", size=30, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            message_text,
            
            ft.Container(height=20),
            ft.Text("➕ THÊM BÀI MỚI", size=20, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            new_chapter,
            new_title,
            new_content,
            ft.Button("Thêm bài", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_add_new),
            
            ft.Container(height=30),
            ft.Divider(),
            ft.Container(height=20),
            
            ft.Text("🗑️ XÓA BÀI", size=20, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
            delete_dropdown,
            ft.Button("Xóa bài", bgcolor="#AA0000", color=ft.Colors.WHITE, on_click=on_delete),
            
            ft.Container(height=30),
            ft.OutlinedButton("Về trang chủ", on_click=lambda e: navigate("home")),
        ]

    def get_cached_lunar_date(date_key: str) -> str:
        """Lấy ngày âm lịch từ cache để không tính lại nhiều lần"""
        if date_key not in _lunar_date_cache:
            _lunar_date_cache[date_key] = build_lunar_date_text()
        return _lunar_date_cache[date_key]

    def open_reader(item: Dict[str, Any]) -> None:
        # Luôn mở bài mới được chọn
        state["current_item"] = item["id"]
        
        try:
            year_value = int((year_field.value or "").strip())
        except ValueError:
            year_value = datetime.now().year
        
        # Lấy ngày âm lịch từ cache
        ngay_am = ngay_am_lich.value or get_cached_lunar_date("today")
        
        # Hiển thị loading message
        show_message("Đang tải bài văn khấn...")
        
        try:
            # Tạo content trong background
            content = personalize_prayer(
                template=item["template"],
                ten_be=ten_be.value or "",
                dia_chi=dia_chi.value or "Quế Võ, Bắc Ninh",
                ngay_thang=ngay_thang.value or datetime.now().strftime("ngày %d/%m/%Y"),
                ngay_am_lich=ngay_am,
                year=year_value,
            )
            print(f"DEBUG: personalize_prayer thành công, length={len(content)}")
        except Exception as e:
            print(f"DEBUG: Lỗi personalize_prayer: {e}")
            content = f"Lỗi khi tải bài: {e}\n\nNội dung gốc:\n{item['template'][:500]}..."
        
        state["title"] = item["title"]
        state["content"] = content
        state["font_size"] = 22
        state["reader_mode"] = True
        state['title_changed'] = True
        
        # Cập nhật reader text
        reader_text.value = content
        reader_text.size = state["font_size"]
        page.update()
        
        # Chuyển sang màn reader
        navigate("reader")
        
        # Xóa loading message
        show_message("Đã tải xong bài văn khấn")

    def adjust_font(delta: int) -> None:
        state["font_size"] = max(16, min(42, state["font_size"] + delta))
        reader_text.size = state["font_size"]
        page.update()

    def render_reader() -> List[ft.Control]:
        # Chỉ tạo lại controls khi cần thiết
        if not hasattr(render_reader, '_controls') or state.get('title_changed', False):
            render_reader._controls = [
                build_top_bar(),
                ft.Text(state["title"] or "Reader Mode", size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                ft.Row(
                    controls=[
                        ft.OutlinedButton("A-", on_click=lambda e: adjust_font(-2)),
                        ft.OutlinedButton("A+", on_click=lambda e: adjust_font(2)),
                        ft.OutlinedButton("Về trang chủ", on_click=lambda e: navigate("home")),
                    ]
                ),
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1, COLOR_ACCENT),
                    border_radius=8,
                    padding=16,
                    content=reader_text,
                ),
            ]
            state['title_changed'] = False
        else:
            # Chỉ cập nhật title khi thay đổi
            render_reader._controls[1].value = state["title"] or "Reader Mode"
            
        return render_reader._controls

    def refresh_screen() -> None:
        current_screen = state["screen"]
        
        # Chỉ skip clean/add khi vẫn ở màn hình reader và không có thay đổi title
        if current_screen == "reader" and hasattr(render_reader, '_controls') and state.get('reader_mode') and not state.get('title_changed', False):
            render_reader._controls[1].value = state["title"] or "Reader Mode"
            return
        
        page.clean()
        if current_screen == "catalog":
            controls = render_catalog()
        elif current_screen == "settings":
            controls = render_settings()
        elif current_screen == "reader":
            controls = render_reader()
        elif current_screen == "editor":
            controls = render_editor()
        else:
            controls = render_home()
        page.add(*controls)
        page.update()

    def navigate(screen_name: str) -> None:
        if screen_name != "reader":
            state["reader_mode"] = False
        state["screen"] = screen_name
        refresh_screen()

    def set_today_lunar() -> None:
        ngay_am_lich.value = build_lunar_date_text()
        page.update()
    
    def update_today() -> None:
        """Cập nhật ngày tháng âm lịch hôm nay"""
        ngay_thang.value = datetime.now().strftime("ngày %d/%m/%Y")
        ngay_am_lich.value = build_lunar_date_text()
        year_field.value = str(datetime.now().year)
        page.update()
        show_message("Đã cập nhật ngày tháng hôm nay")

    def on_search_change(_: ft.ControlEvent) -> None:
        state["search"] = (search_field.value or "").strip()
        if state["screen"] == "catalog":
            refresh_screen()

    def parse_solar_input(value: str) -> datetime | None:
        raw = (value or "").strip().lower()
        if not raw:
            return None
        raw = raw.replace("ngày", "").strip()
        match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw)
        if not match:
            return None
        try:
            day, month, year = map(int, match.groups())
            return datetime(year, month, day)
        except ValueError:
            return None

    def on_solar_date_change(_: ft.ControlEvent) -> None:
        dt = parse_solar_input(ngay_thang.value or "")
        if dt is None:
            return
        ngay_am_lich.value = build_lunar_date_text(dt)
        page.update()

    ngay_thang.on_change = on_solar_date_change
    search_field.on_change = on_search_change

    navigate("home")


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)
