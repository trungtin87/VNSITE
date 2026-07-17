# -*- coding: utf-8 -*-
"""
loc.py — Bộ lọc (filter) cho template, cú pháp giống Liquid: {{ bien | ten_loc }}

Có thể nối nhiều lọc: {{ bien | loc_1 | loc_2: "doi_so" }}
Mỗi hàm lọc có chữ ký thống nhất: loc(gia_tri, doi_so, context) -> gia_tri_moi
  - gia_tri: giá trị hiện tại đang được lọc (kết quả lọc trước, hoặc giá trị gốc)
  - doi_so:  chuỗi đối số sau dấu ":" nếu có, ví dụ {{ x | rut_gon: "20" }} -> doi_so = "20"
  - context: toàn bộ ngữ cảnh đang render (dùng cho lọc cần biết cau_hinh, vd baseurl)
"""
import re
from datetime import datetime

from .slug import chuyen_thanh_slug

_RE_THE_HTML = re.compile(r"<[^>]+>")


def _ve_chuoi(gia_tri) -> str:
    return "" if gia_tri is None else str(gia_tri)


def loc_duong_dan(gia_tri, doi_so, context):
    """{{ "/du-an/x" | duong_dan }} -> chèn cau_hinh.baseurl phía trước.
    Đây là cách ĐÚNG và AN TOÀN để chèn baseurl — dùng lọc này thay vì tự gõ
    "{{ cau_hinh.baseurl }}{{ x }}" ở khắp nơi để tránh quên (nguyên nhân phổ
    biến nhất gây lỗi ảnh/link 404 khi deploy project site)."""
    baseurl = ""
    if context:
        cau_hinh = context.get("cau_hinh") or {}
        baseurl = cau_hinh.get("baseurl") or ""
    duong_dan = _ve_chuoi(gia_tri)
    if duong_dan.startswith("http://") or duong_dan.startswith("https://") or duong_dan.startswith("//"):
        return duong_dan  # link ngoài, không đụng vào
    if not duong_dan.startswith("/"):
        duong_dan = "/" + duong_dan
    return baseurl + duong_dan


def loc_mac_dinh(gia_tri, doi_so, context):
    """{{ x | mac_dinh: "chuoi neu rong" }}"""
    if gia_tri in (None, "", [], {}):
        return doi_so or ""
    return gia_tri


def loc_hoa(gia_tri, doi_so, context):
    return _ve_chuoi(gia_tri).upper()


def loc_thuong(gia_tri, doi_so, context):
    return _ve_chuoi(gia_tri).lower()


def loc_hoa_dau(gia_tri, doi_so, context):
    s = _ve_chuoi(gia_tri)
    return s[:1].upper() + s[1:] if s else s


def loc_rut_gon(gia_tri, doi_so, context):
    """{{ mo_ta | rut_gon: "20" }} -> cắt còn 20 từ, thêm "…" nếu dài hơn."""
    so_tu = int(doi_so) if doi_so else 30
    tu = _ve_chuoi(gia_tri).split()
    if len(tu) <= so_tu:
        return " ".join(tu)
    return " ".join(tu[:so_tu]) + "…"


def loc_rut_gon_ky_tu(gia_tri, doi_so, context):
    """{{ mo_ta | rut_gon_ky_tu: "100" }} -> cắt còn 100 ký tự."""
    so_ky_tu = int(doi_so) if doi_so else 100
    s = _ve_chuoi(gia_tri)
    return s if len(s) <= so_ky_tu else s[:so_ky_tu] + "…"


def loc_dem(gia_tri, doi_so, context):
    """{{ danh_sach | dem }} -> số phần tử / độ dài chuỗi."""
    try:
        return len(gia_tri)
    except TypeError:
        return 0


def loc_noi(gia_tri, doi_so, context):
    """{{ danh_sach | noi: ", " }} -> nối các phần tử bằng dấu phân cách."""
    phan_cach = doi_so if doi_so is not None else ", "
    if not gia_tri:
        return ""
    return phan_cach.join(_ve_chuoi(x) for x in gia_tri)


def loc_dinh_dang_ngay(gia_tri, doi_so, context):
    """{{ ngay | dinh_dang_ngay: "%d/%m/%Y" }}
    Nhận vào chuỗi ISO (yyyy-mm-dd hoặc yyyy-mm-dd HH:MM:SS) hoặc datetime."""
    mau = doi_so or "%d/%m/%Y"
    if isinstance(gia_tri, datetime):
        dt = gia_tri
    else:
        s = _ve_chuoi(gia_tri).strip()
        dt = None
        for dinh_dang_thu in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, dinh_dang_thu)
                break
            except ValueError:
                continue
        if dt is None:
            return s  # không parse được thì trả nguyên văn, không crash
    return dt.strftime(mau)


def loc_slug(gia_tri, doi_so, context):
    return chuyen_thanh_slug(_ve_chuoi(gia_tri))


def loc_bo_the_html(gia_tri, doi_so, context):
    return _RE_THE_HTML.sub("", _ve_chuoi(gia_tri))


def loc_dau_tien(gia_tri, doi_so, context):
    try:
        return gia_tri[0]
    except (IndexError, TypeError, KeyError):
        return None


def loc_cuoi_cung(gia_tri, doi_so, context):
    try:
        return gia_tri[-1]
    except (IndexError, TypeError, KeyError):
        return None


def loc_dinh_dang_gia(gia_tri, doi_so, context):
    """{{ gia | dinh_dang_gia }} -> "250.000đ" (chấm ngăn cách hàng nghìn kiểu Việt Nam)."""
    try:
        so = int(float(gia_tri))
    except (TypeError, ValueError):
        return _ve_chuoi(gia_tri)
    return f"{so:,}".replace(",", ".") + "đ"


def loc_ma_hoa_url(gia_tri, doi_so, context):
    """{{ ten | ma_hoa_url }} -> mã hoá để nhét an toàn vào query string
    (dùng khi điền sẵn giá trị có dấu/khoảng trắng vào link Google Form)."""
    import urllib.parse
    return urllib.parse.quote(_ve_chuoi(gia_tri))


BO_LOC = {
    "duong_dan": loc_duong_dan,
    "url": loc_duong_dan,  # bí danh, quen thuộc với người từng dùng Jekyll
    "mac_dinh": loc_mac_dinh,
    "hoa": loc_hoa,
    "thuong": loc_thuong,
    "hoa_dau": loc_hoa_dau,
    "rut_gon": loc_rut_gon,
    "rut_gon_ky_tu": loc_rut_gon_ky_tu,
    "dem": loc_dem,
    "noi": loc_noi,
    "dinh_dang_ngay": loc_dinh_dang_ngay,
    "dinh_dang_gia": loc_dinh_dang_gia,
    "ma_hoa_url": loc_ma_hoa_url,
    "slug": loc_slug,
    "bo_the_html": loc_bo_the_html,
    "dau_tien": loc_dau_tien,
    "cuoi_cung": loc_cuoi_cung,
}
