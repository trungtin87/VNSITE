# -*- coding: utf-8 -*-
"""content.py — Đọc & xử lý 1 file nội dung (.md): front matter + markdown + các phép tính phụ."""
import os
import re
import yaml
import markdown as md_lib
from datetime import datetime

from .loi import LoiFrontMatter
from .slug import chuyen_thanh_slug

_RE_FRONT_MATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
_MARKER_TOMTAT = "<!--tomtat-->"

_TIEN_ICH_MARKDOWN = ["extra", "toc", "codehilite", "sane_lists"]


def dam_bao_co_front_matter(duong_dan_file: str, loai: str = "bai_viet") -> bool:
    """Nếu file .md CHƯA có front matter (không mở đầu bằng '---'), tự sinh 1
    khối front matter tối thiểu rồi GHI THẲNG vào file:
        - tieu_de: suy ra từ TÊN FILE (bỏ tiền tố ngày YYYY-MM-DD- nếu có,
          đổi "-"/"_" thành khoảng trắng, viết hoa chữ đầu)
        - ngay: thời điểm NGAY LÚC BUILD (không phải ngày tạo file trên đĩa)
        - (dự án) mo_ta_ngan: lấy tạm đoạn văn đầu tiên trong nội dung

    Đây chỉ là bản NHÁP để build không bị chặn — người dùng nên tự mở file
    sửa lại cho đúng ý. Nếu file đã có front matter hợp lệ, KHÔNG đụng vào.

    Trả về True nếu vừa tự sinh (để builder.py log lại cho người dùng biết),
    False nếu file đã có front matter từ trước.
    """
    with open(duong_dan_file, "r", encoding="utf-8") as f:
        toan_van = f.read()

    if _RE_FRONT_MATTER.match(toan_van):
        return False  # đã có front matter -> không đụng vào

    ten_file = os.path.splitext(os.path.basename(duong_dan_file))[0]
    m_ngay_trong_ten = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", ten_file)
    phan_ten = m_ngay_trong_ten.group(4) if m_ngay_trong_ten else ten_file
    tieu_de_doan = phan_ten.replace("-", " ").replace("_", " ").strip()
    tieu_de_tu_dong = (tieu_de_doan[:1].upper() + tieu_de_doan[1:]) if tieu_de_doan else "Chưa đặt tiêu đề"

    fm = {
        "tieu_de": tieu_de_tu_dong,
        "ngay": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if loai == "du_an":
        doan_dau = re.sub(r"\s+", " ", toan_van.strip().split("\n\n")[0]).strip()
        fm["mo_ta_ngan"] = doan_dau[:120] if doan_dau else "Chưa có mô tả — hãy sửa lại."

    khoi_yaml = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    noi_dung_moi = f"---\n{khoi_yaml}\n---\n\n{toan_van}"
    with open(duong_dan_file, "w", encoding="utf-8") as f:
        f.write(noi_dung_moi)
    return True


def doc_front_matter(duong_dan_file: str):
    """Trả về (front_matter: dict, noi_dung_markdown: str)."""
    with open(duong_dan_file, "r", encoding="utf-8") as f:
        toan_van = f.read()
    m = _RE_FRONT_MATTER.match(toan_van)
    if not m:
        raise LoiFrontMatter(duong_dan_file, "--- front matter ---")
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def kiem_tra_truong_bat_buoc(fm: dict, duong_dan_file: str, cac_truong: list):
    for truong in cac_truong:
        if truong not in fm or fm[truong] in (None, ""):
            raise LoiFrontMatter(duong_dan_file, truong)


def render_markdown(noi_dung_md: str) -> str:
    return md_lib.markdown(noi_dung_md, extensions=_TIEN_ICH_MARKDOWN)


def tinh_excerpt(noi_dung_md: str, so_tu_mac_dinh: int) -> str:
    """Excerpt tự động: dùng marker <!--tomtat--> nếu có, ngược lại cắt N từ đầu."""
    if _MARKER_TOMTAT in noi_dung_md:
        phan_dau = noi_dung_md.split(_MARKER_TOMTAT, 1)[0]
        return render_markdown(phan_dau.strip())

    tu = noi_dung_md.split()
    phan_dau = " ".join(tu[:so_tu_mac_dinh])
    if len(tu) > so_tu_mac_dinh:
        phan_dau += "…"
    return render_markdown(phan_dau)


def tinh_thoi_gian_doc(noi_dung_md: str, so_tu_moi_phut: int) -> int:
    so_tu = len(noi_dung_md.split())
    phut = max(1, round(so_tu / so_tu_moi_phut))
    return phut


def lay_slug(fm: dict, duong_dan_file: str) -> str:
    if fm.get("slug"):
        return chuyen_thanh_slug(str(fm["slug"]))
    ten_file = os.path.splitext(os.path.basename(duong_dan_file))[0]
    # Bỏ tiền tố ngày YYYY-MM-DD- nếu có, giữ lại phần tiêu đề để tạo slug từ chính nó
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", ten_file)
    goc = m.group(1) if m else ten_file
    if fm.get("tieu_de"):
        return chuyen_thanh_slug(str(fm["tieu_de"]))
    return chuyen_thanh_slug(goc)
