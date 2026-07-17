# -*- coding: utf-8 -*-
"""rss.py — Sinh rss.xml (RSS 2.0) từ danh sách bài viết mới nhất."""
from datetime import datetime
from xml.sax.saxutils import escape

_TEN_THANG = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_TEN_THU = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _ve_rfc822(ngay_str: str) -> str:
    """Chuyển 'YYYY-MM-DD' hoặc 'YYYY-MM-DD HH:MM:SS' -> định dạng RFC 822
    mà chuẩn RSS yêu cầu cho <pubDate>. Không parse được thì trả chuỗi rỗng
    (bỏ qua thẻ pubDate) thay vì làm hỏng cả file XML."""
    s = (ngay_str or "").strip()
    dt = None
    for dinh_dang in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, dinh_dang)
            break
        except ValueError:
            continue
    if dt is None:
        return ""
    return (f"{_TEN_THU[dt.weekday()]}, {dt.day:02d} {_TEN_THANG[dt.month - 1]} {dt.year} "
            f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} +0000")


def sinh_rss(cau_hinh: dict, tat_ca_bai: list, excerpt_thanh_text_fn, so_bai_toi_da: int = 20) -> str:
    goc = (cau_hinh.get("url") or "").rstrip("/")
    baseurl = cau_hinh.get("baseurl") or ""
    link_site = f"{goc}{baseurl}/"

    dong = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        f"<title>{escape(cau_hinh.get('ten_trangweb', ''))}</title>",
        f"<link>{escape(link_site)}</link>",
        f"<description>{escape(cau_hinh.get('mo_ta', ''))}</description>",
        f"<language>{escape(cau_hinh.get('ngon_ngu', 'vi'))}</language>",
    ]
    for bai in tat_ca_bai[:so_bai_toi_da]:
        link = f"{goc}{baseurl}{bai['url']}"
        dong.append("<item>")
        dong.append(f"  <title>{escape(bai['tieu_de'])}</title>")
        dong.append(f"  <link>{escape(link)}</link>")
        dong.append(f"  <guid isPermaLink=\"true\">{escape(link)}</guid>")
        dong.append(f"  <description>{escape(excerpt_thanh_text_fn(bai.get('excerpt', '')))}</description>")
        pub = _ve_rfc822(bai.get("ngay", ""))
        if pub:
            dong.append(f"  <pubDate>{pub}</pubDate>")
        dong.append("</item>")
    dong.append("</channel></rss>")
    return "\n".join(dong)
