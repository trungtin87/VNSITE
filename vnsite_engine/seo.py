# -*- coding: utf-8 -*-
"""seo.py — Sinh thẻ <meta> Open Graph + Twitter Card cho mỗi trang."""
import html


def sinh_the_seo(cau_hinh: dict, tieu_de: str, mo_ta: str, url_trang: str, anh: str = None) -> str:
    anh = anh or cau_hinh.get("anh_mac_dinh", "")
    goc = cau_hinh.get("url", "").rstrip("/")
    url_day_du = f"{goc}{url_trang}" if goc else url_trang
    anh_day_du = f"{goc}{anh}" if (goc and anh and not anh.startswith("http")) else anh

    def esc(s):
        return html.escape(s or "", quote=True)

    dong = [
        f'<meta property="og:title" content="{esc(tieu_de)}">',
        f'<meta property="og:description" content="{esc(mo_ta)}">',
        f'<meta property="og:type" content="article">',
        f'<meta property="og:url" content="{esc(url_day_du)}">',
    ]
    if anh_day_du:
        dong.append(f'<meta property="og:image" content="{esc(anh_day_du)}">')

    dong += [
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(tieu_de)}">',
        f'<meta name="twitter:description" content="{esc(mo_ta)}">',
    ]
    if anh_day_du:
        dong.append(f'<meta name="twitter:image" content="{esc(anh_day_du)}">')

    return "\n    ".join(dong)
