# -*- coding: utf-8 -*-
"""
server.py — Dev server cục bộ + watch file, tự rebuild khi lưu (mục VIII của đặc tả).

Không phụ thuộc thư viện ngoài: chỉ dùng http.server (built-in) để phục vụ file tĩnh,
và polling mtime (built-in os) để theo dõi thay đổi — không cần watchdog.
"""
import functools
import http.server
import os
import socketserver
import threading
import time

from .builder import build
from .loi import LoiVNSITE

_CAC_THU_MUC_THEO_DOI = [
    "_bocuctrang", "_thanhphantrang", "_cacbaiviet", "_duan",
    "tainguyen", "_dulieu",
]
_CAC_FILE_THEO_DOI_O_GOC = ["_cauhinhtrangweb.yml"]


def _quet_dau_van_tay(duong_dan_goc: str) -> dict:
    """Trả về dict {duong_dan_file: mtime} cho mọi file cần theo dõi."""
    dau_van_tay = {}
    for ten_file in _CAC_FILE_THEO_DOI_O_GOC:
        duong_dan = os.path.join(duong_dan_goc, ten_file)
        if os.path.isfile(duong_dan):
            dau_van_tay[duong_dan] = os.path.getmtime(duong_dan)

    for ten_file in os.listdir(duong_dan_goc):
        if ten_file.endswith(".html"):
            dau_van_tay[ten_file] = os.path.getmtime(os.path.join(duong_dan_goc, ten_file))

    for thu_muc in _CAC_THU_MUC_THEO_DOI:
        duong_dan_thu_muc = os.path.join(duong_dan_goc, thu_muc)
        if not os.path.isdir(duong_dan_thu_muc):
            continue
        for goc, _dirs, files in os.walk(duong_dan_thu_muc):
            for ten_file in files:
                duong_dan = os.path.join(goc, ten_file)
                dau_van_tay[duong_dan] = os.path.getmtime(duong_dan)
    return dau_van_tay


def _luong_theo_doi(duong_dan_goc, che_do_preview, khoang_nghi=1.0):
    dau_van_tay_truoc = _quet_dau_van_tay(duong_dan_goc)
    while True:
        time.sleep(khoang_nghi)
        try:
            dau_van_tay_sau = _quet_dau_van_tay(duong_dan_goc)
        except FileNotFoundError:
            continue  # file đang được ghi dở, thử lại ở vòng sau
        if dau_van_tay_sau != dau_van_tay_truoc:
            print("\n[VNSITE] Phát hiện thay đổi → rebuild...")
            try:
                build(duong_dan_goc, che_do_preview=che_do_preview)
            except LoiVNSITE as loi:
                print(f"[VNSITE] {loi}")
            except Exception as loi:  # không để watcher chết vì 1 lỗi build
                print(f"[VNSITE] Lỗi build không mong muốn: {loi}")
            dau_van_tay_truoc = dau_van_tay_sau


def chay_dev_server(duong_dan_goc: str, cong: int = 8000, che_do_preview: bool = False):
    from .config import doc_cau_hinh
    cau_hinh = doc_cau_hinh(duong_dan_goc)
    thu_muc_output = os.path.join(duong_dan_goc, cau_hinh["thu_muc_output"])

    print("[VNSITE] Build lần đầu...")
    build(duong_dan_goc, che_do_preview=che_do_preview)

    luong = threading.Thread(
        target=_luong_theo_doi, args=(duong_dan_goc, che_do_preview), daemon=True
    )
    luong.start()

    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=thu_muc_output)
    with socketserver.TCPServer(("", cong), Handler) as httpd:
        print(f"[VNSITE] Đang phục vụ tại http://localhost:{cong}/  (Ctrl+C để dừng)")
        print(f"[VNSITE] Đang theo dõi thay đổi file để tự rebuild...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[VNSITE] Đã dừng dev server.")
