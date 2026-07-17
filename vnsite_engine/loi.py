# -*- coding: utf-8 -*-
"""
loi.py — Định nghĩa các lỗi build của VNSITE.

Mục tiêu (đặc tả mục II.7): mọi lỗi cấu hình/nội dung phải dừng build với
thông báo RÕ RÀNG (tên file, vị trí, nguyên nhân) — không được crash im lặng
bằng traceback khó hiểu, và không được âm thầm bỏ qua.
"""


class LoiVNSITE(Exception):
    """Lớp lỗi gốc cho mọi lỗi phát sinh trong quá trình build VNSITE."""
    pass


class LoiFrontMatter(LoiVNSITE):
    def __init__(self, duong_dan_file, truong_thieu):
        self.duong_dan_file = duong_dan_file
        self.truong_thieu = truong_thieu
        super().__init__(
            f"[LỖI FRONT MATTER] File '{duong_dan_file}' thiếu trường bắt buộc: "
            f"'{truong_thieu}'. Vui lòng thêm trường này vào phần front matter "
            f"(giữa hai dòng '---') ở đầu file."
        )


class LoiIncludeKhongTonTai(LoiVNSITE):
    def __init__(self, ten_component, file_goi, dong=None):
        vi_tri = f" (dòng {dong})" if dong else ""
        super().__init__(
            f"[LỖI NHÚNG COMPONENT] Không tìm thấy file '{ten_component}' "
            f"trong thư mục '_thanhphantrang/'. Lỗi này xảy ra khi xử lý file "
            f"'{file_goi}'{vi_tri}. Kiểm tra lại tên file hoặc chính tả (có dấu/không dấu)."
        )


class LoiLayoutKhongTonTai(LoiVNSITE):
    def __init__(self, ten_layout, file_goi):
        super().__init__(
            f"[LỖI KẾ THỪA LAYOUT] Không tìm thấy layout '{ten_layout}' "
            f"trong thư mục '_bocuctrang/'. Lỗi này xảy ra khi xử lý file '{file_goi}'."
        )


class LoiTrungSlug(LoiVNSITE):
    def __init__(self, slug, file_1, file_2):
        super().__init__(
            f"[CẢNH BÁO TRÙNG SLUG] Hai bài viết có cùng slug '{slug}':\n"
            f"    - {file_1}\n    - {file_2}\n"
            f"  → Bài xuất bản sau sẽ ghi đè bài trước trong '_ketqua/'. "
            f"Hãy đổi tiêu đề hoặc thêm trường 'slug' riêng cho một trong hai bài."
        )
