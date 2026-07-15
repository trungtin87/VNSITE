# -*- coding: utf-8 -*-
"""config.py — Đọc _cauhinhtrangweb.yml và các file dữ liệu trong _dulieu/*.yml"""
import os
import yaml


def doc_cau_hinh(duong_dan_goc: str) -> dict:
    duong_dan = os.path.join(duong_dan_goc, "_cauhinhtrangweb.yml")
    if not os.path.isfile(duong_dan):
        raise FileNotFoundError(
            f"[LỖI CẤU HÌNH] Không tìm thấy file '_cauhinhtrangweb.yml' ở '{duong_dan_goc}'. "
            f"Đây là file bắt buộc phải có ở gốc dự án."
        )
    with open(duong_dan, "r", encoding="utf-8") as f:
        cau_hinh = yaml.safe_load(f) or {}

    # Giá trị mặc định an toàn để phần còn lại của chương trình không cần kiểm tra None liên tục
    cau_hinh.setdefault("ten_trangweb", "Trang web của tôi")
    cau_hinh.setdefault("mo_ta", "")
    cau_hinh.setdefault("url", "")
    cau_hinh.setdefault("baseurl", "")
    cau_hinh.setdefault("ngon_ngu", "vi")
    cau_hinh.setdefault("thu_muc_output", "_ketqua")
    cau_hinh.setdefault("so_tu_moi_phut_doc", 200)
    cau_hinh.setdefault("so_tu_tomtat_mac_dinh", 60)
    cau_hinh.setdefault("dieu_huong", [])
    cau_hinh.setdefault("mang_xa_hoi", {})
    cau_hinh.setdefault("giscus", {"bat": False})
    cau_hinh.setdefault("tim_kiem", {"bat": False})
    return cau_hinh


def doc_du_lieu(duong_dan_goc: str) -> dict:
    """Đọc mọi file *.yml trong _dulieu/ thành dict: du_lieu['thanh_vien'], du_lieu['ho_so'], ..."""
    thu_muc = os.path.join(duong_dan_goc, "_dulieu")
    ket_qua = {}
    if not os.path.isdir(thu_muc):
        return ket_qua
    for ten_file in sorted(os.listdir(thu_muc)):
        if ten_file.endswith((".yml", ".yaml")):
            khoa = os.path.splitext(ten_file)[0]
            with open(os.path.join(thu_muc, ten_file), "r", encoding="utf-8") as f:
                ket_qua[khoa] = yaml.safe_load(f) or {}
    return ket_qua
