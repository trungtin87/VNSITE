# -*- coding: utf-8 -*-
"""
favicon.py — Tự sinh favicon nhiều kích thước từ 1 ảnh gốc (mục VII, 🟢 tùy chọn).

Cần thư viện Pillow (đã có sẵn trong môi trường build phổ biến). Nếu người dùng
không có Pillow, hàm sẽ bỏ qua và in hướng dẫn thay vì làm crash toàn bộ build.
"""
import os

_CAC_KICH_THUOC = [16, 32, 180, 192, 512]


def sinh_favicon(duong_dan_goc: str, im_lang: bool = False) -> bool:
    def log(msg):
        if not im_lang:
            print(msg)

    duong_dan_nguon = os.path.join(duong_dan_goc, "tainguyen", "hinhanh", "favicon-nguon.png")
    if not os.path.isfile(duong_dan_nguon):
        log("[VNSITE] Không tìm thấy 'tainguyen/hinhanh/favicon-nguon.png' — bỏ qua sinh favicon.")
        return False

    try:
        from PIL import Image
    except ImportError:
        log(
            "[VNSITE] Chưa cài Pillow nên không thể tự sinh favicon.\n"
            "         Cài bằng: pip install Pillow --break-system-packages"
        )
        return False

    thu_muc_dich = os.path.join(duong_dan_goc, "tainguyen", "hinhanh")
    anh_goc = Image.open(duong_dan_nguon).convert("RGBA")

    for kich_thuoc in _CAC_KICH_THUOC:
        anh_resize = anh_goc.resize((kich_thuoc, kich_thuoc), Image.LANCZOS)
        anh_resize.save(os.path.join(thu_muc_dich, f"favicon-{kich_thuoc}.png"))

    # favicon.png mặc định (dùng trong thẻ <link rel="icon"> ở trangmacdinh.html)
    anh_goc.resize((32, 32), Image.LANCZOS).save(os.path.join(thu_muc_dich, "favicon.png"))

    log(f"[VNSITE] Đã sinh {len(_CAC_KICH_THUOC) + 1} favicon từ favicon-nguon.png")
    return True
