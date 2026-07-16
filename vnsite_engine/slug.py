# -*- coding: utf-8 -*-
"""
slug.py — Chuyển đổi chuỗi tiếng Việt có dấu thành slug an toàn cho URL/tên file.

Xử lý theo đúng mục II.3 của đặc tả:
  - Bỏ dấu bằng unicodedata.normalize('NFD') rồi loại các ký tự tổ hợp (combining marks)
  - Xử lý riêng chữ "đ"/"Đ" (không bị NFD tách dấu như các nguyên âm khác)
  - Hạ chữ thường
  - Thay khoảng trắng và ký tự đặc biệt bằng dấu gạch ngang "-"
  - Gộp nhiều dấu "-" liên tiếp, bỏ dấu "-" ở đầu/cuối
"""
import re
import unicodedata

_BANG_DAC_BIET = str.maketrans({
    "đ": "d", "Đ": "D",
})


def chuyen_thanh_slug(chuoi: str) -> str:
    """Chuyển một chuỗi tiếng Việt bất kỳ thành slug dạng: vi-du-tieu-de-bai-viet"""
    if not chuoi:
        return ""

    # 1. Xử lý riêng đ/Đ trước khi NFD (vì NFD không tách được đ thành d + dấu)
    chuoi = chuoi.translate(_BANG_DAC_BIET)

    # 2. Bỏ dấu thanh + dấu mũ/móc bằng NFD rồi loại bỏ các ký tự tổ hợp (category Mn)
    chuoi = unicodedata.normalize("NFD", chuoi)
    chuoi = "".join(ky_tu for ky_tu in chuoi if unicodedata.category(ky_tu) != "Mn")
    chuoi = unicodedata.normalize("NFC", chuoi)

    # 3. Hạ chữ thường
    chuoi = chuoi.lower()

    # 4. Thay mọi ký tự không phải chữ/số bằng "-"
    chuoi = re.sub(r"[^a-z0-9]+", "-", chuoi)

    # 5. Gộp nhiều "-" liên tiếp, bỏ "-" ở đầu/cuối
    chuoi = re.sub(r"-+", "-", chuoi).strip("-")

    return chuoi


if __name__ == "__main__":
    # Vài phép thử nhanh
    vi_du = [
        "Hướng Dẫn Dùng Jekyll Cho Người Việt",
        "Đây Là Đường Dẫn Có Đ",
        "  Nhiều   khoảng   trắng  ",
        "C++ & Python: So sánh 2026",
    ]
    for v in vi_du:
        print(f"{v!r:45} -> {chuyen_thanh_slug(v)}")
