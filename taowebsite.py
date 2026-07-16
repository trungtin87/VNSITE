#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
taowebsite.py — Điểm vào CLI của VNSITE.

Cách dùng:
    python taowebsite.py build              Build 1 lần ra _ketqua/
    python taowebsite.py build --preview     Build kèm cả bài viết nháp (nhap: true)
    python taowebsite.py serve               Dev server local + tự rebuild khi lưu file
    python taowebsite.py serve --port 9000   Đổi cổng phục vụ (mặc định 8000)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vnsite_engine.builder import build
from vnsite_engine.server import chay_dev_server
from vnsite_engine.favicon import sinh_favicon
from vnsite_engine.loi import LoiVNSITE


def main():
    parser = argparse.ArgumentParser(
        prog="taowebsite.py",
        description="VNSITE — Trình tạo website tĩnh tự động cho người Việt",
    )
    lenh_con = parser.add_subparsers(dest="lenh", required=True)

    p_build = lenh_con.add_parser("build", help="Build trang web ra thư mục output")
    p_build.add_argument("--preview", action="store_true", help="Bao gồm cả bài viết nháp (nhap: true)")

    p_serve = lenh_con.add_parser("serve", help="Chạy dev server local, tự rebuild khi lưu file")
    p_serve.add_argument("--port", type=int, default=8000, help="Cổng phục vụ (mặc định: 8000)")
    p_serve.add_argument("--preview", action="store_true", help="Bao gồm cả bài viết nháp trong lúc xem trước")

    lenh_con.add_parser("favicon", help="Tự sinh favicon nhiều kích thước từ tainguyen/hinhanh/favicon-nguon.png")

    doi_so = parser.parse_args()
    duong_dan_goc = os.path.dirname(os.path.abspath(__file__))

    try:
        if doi_so.lenh == "build":
            build(duong_dan_goc, che_do_preview=doi_so.preview)
        elif doi_so.lenh == "serve":
            chay_dev_server(duong_dan_goc, cong=doi_so.port, che_do_preview=doi_so.preview)
        elif doi_so.lenh == "favicon":
            sinh_favicon(duong_dan_goc)
    except LoiVNSITE as loi:
        # Lỗi nghiệp vụ đã được định nghĩa rõ ràng (mục II.7) -> in gọn, không in traceback
        print(f"\n{loi}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
