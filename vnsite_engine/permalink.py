# -*- coding: utf-8 -*-
"""
permalink.py — Sinh đường dẫn (URL) từ mẫu permalink cấu hình được trong
_cauhinhtrangweb.yml, giống cơ chế `permalink:` của Jekyll.

Mẫu dùng dấu ":" trước tên biến, ví dụ:
    "/:chuyen_muc/:nam/:thang/:slug/"
    "/du-an/:slug/"
    "/tag/:slug/"

Trước bản này, mỗi loại URL (bài viết/dự án/tag) bị viết CỨNG bằng f-string
rải rác trong builder.py — muốn đổi cấu trúc URL phải sửa nhiều nơi, dễ sót.
Giờ chỉ cần đổi 1 dòng trong _cauhinhtrangweb.yml.
"""
import re

_RE_GOP_GACH_CHEO = re.compile(r"/+")


def sinh_permalink(mau: str, **bien) -> str:
    """Thay từng ':ten_bien' trong mẫu bằng giá trị tương ứng.
    Luôn trả về dạng có gạch chéo ở đầu và cuối, không có gạch chéo đôi."""
    ket_qua = mau
    for ten, gia_tri in bien.items():
        ket_qua = ket_qua.replace(f":{ten}", str(gia_tri))
    ket_qua = _RE_GOP_GACH_CHEO.sub("/", ket_qua)
    if not ket_qua.startswith("/"):
        ket_qua = "/" + ket_qua
    if not ket_qua.endswith("/"):
        ket_qua += "/"
    return ket_qua
