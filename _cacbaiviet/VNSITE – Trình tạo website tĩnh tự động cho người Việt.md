# BẢN ĐẶC TẢ DỰ ÁN: VNSITE

**Tên dự án:** VNSITE – Trình tạo website tĩnh tự động cho người Việt

**Ngôn ngữ phát triển:** Python (tối thiểu 3.8+)

**Triết lý thiết kế:** Component-driven (Phát triển dựa trên thành phần độc lập), Bản địa hóa (Sử dụng tên thư mục tiếng Việt thân thiện).

## I. KIẾN TRÚC THƯ MỤC NGUỒN (SOURCE TREE)

Hệ thống quản lý mã nguồn đầu vào theo sơ đồ phân cấp dưới đây:

Plaintext

```
thu_muc_du_an_VNSITE/
│
├── _cauhinhtrangweb.yml      # Cấu hình toàn cục hệ thống (YAML)
├── taowebsite.py          # Lõi xử lý logic biên dịch biên dịch chính (Python)
│
├── _bocuctrang/             # Khung xương giao diện tổng thể (Layouts)
│   ├── trangmacdinh.html    # Khung bao quát <html>, <head>, <body>
│   ├── baiviet.html         # Khung kế thừa hiển thị nội dung bài viết chi tiết
│   └── trangweb.html        # Khung kế thừa hiển thị các trang tĩnh độc lập
│
├── _thanhphantrang/         # Các khối giao diện phân rã nhỏ lẻ (Components)
│   ├── phandautrang.html    # Khối Header
│   ├── thanhdieuhuong.html  # Khối Menu điều hướng Nav
│   ├── phanchantrang.html   # Khối Footer
│   └── thanhben.html        # Khối Sidebar
│
├── _cacbaiviet/             # Thư mục nội dung viết bằng Markdown (.md)
│   ├── 2026-07-10-bai-viet-thu-nhat.md
│   └── 2026-07-13-huong-dan-jekyll.md
│
├── tainguyen/               # Tài nguyên tĩnh của giao diện (Assets)
│   ├── css/
│   │   └── main.scss        # Tệp gom tụ kiểu dáng hoặc chứa SCSS mặc định
│   └── hinhanh/             # Nơi lưu trữ hình ảnh của trang web
│
└── _dulieu/                 # Cơ sở dữ liệu thô dạng danh sách (Data)
    └── thanh_vien.yml       # Dữ liệu có cấu trúc phục vụ vòng lặp xuất HTML
```

## II. ĐẶC TẢ CHI TIẾT CÁC THÀNH PHẦN CỐT LÕI

### 1. Tệp Cấu hình `_cauhinhtrangweb.yml`

Là nơi lưu trữ toàn bộ tham số điều hướng cấu hình và các biến tự định nghĩa toàn cục. Khi thay đổi tệp này, toàn bộ giao diện xuất bản sẽ thay đổi theo.

- **Các trường bắt buộc:** `title` (Tiêu đề), `url` (Tên miền chính), `destination` (Thư mục đích xuất bản).
    
- **Tiện ích tích hợp (Plugins):** Khai báo các module bổ sung bao gồm `VNSITE-RSS`, `VNSITE-sitemap`, và `VNSITE-phan_trang`.
    

### 2. Định dạng Bài viết (Front Matter & Markdown)

Mỗi tệp trong thư mục `_cacbaiviet/` bắt buộc phải đặt tên theo quy tắc ngày tháng: `NĂM-THÁNG-NGÀY-tieu-de.md`.

Đầu mỗi tệp phải có phần cấu hình dữ liệu được bao bọc bởi 3 dấu gạch ngang (`---`):

YAML

```
---
tieu_de: "Hướng dẫn cài đặt Python"
ngay_dang: "2026-07-13"
bocuc: "baiviet"
---
Nội dung bài viết bằng chữ thô Markdown ở đây...
```

### 3. Quy ước thẻ nhúng Thành phần (Liquid-like Tags)

Để ghép các mảnh giao diện từ `_thanhphantrang/` vào `_bocuctrang/`, hệ thống sử dụng cú pháp thẻ nhúng tùy biến dạng:

- `{% nhung phandautrang.html %}`: Ra lệnh cho Python đọc tệp tương ứng trong thư mục thành phần để dán đè nội dung vào vị trí này.
    
- `{{ noi_dung }}`: Thẻ giữ chỗ để đổ nội dung sau khi chuyển đổi từ Markdown sang HTML.
    

## III. QUY TRÌNH BIÊN DỊCH VÀ ĐÓNG GÓI CỦA `taowebsite.py`

Khi người dùng thực thi lệnh `python taowebsite.py`, hệ thống xử lý logic qua 5 bước nghiêm ngặt sau:

Plaintext

```
[Bắt đầu]
    │
    ▼
[Bước 1: Làm sạch] ──> Xóa và khởi tạo lại thư mục xuất bản 'trangwebxuatban/'
    │
    ▼
[Bước 2: Đọc cấu hình] ──> Dùng PyYAML nạp file '_cauhinhtrangweb.yml'
    │
    ▼
[Bước 3: Xử lý CSS/Style] ──> Quét thẻ <style> từ '_thanhphantrang/', bóc tách bằng Regex,
    │                         gom nội dung nối vào 'tainguyen/css/main.scss'
    │
    ▼
[Bước 4: Trộn Layout & Bài viết] ──> Dịch Markdown -> HTML. 
    │                              Trộn dữ liệu Front Matter vào khung của '_bocuctrang'
    │
    ▼
[Bước 5: Xuất bản dữ liệu] ──> Ghi file HTML hoàn chỉnh và sao chép toàn bộ 
                               thư mục 'tainguyen/' vào 'trangwebxuatban/'
```

### Chi tiết kỹ thuật xử lý tại Bước 3 (Gom tách CSS tự động):

Để đảm bảo lập trình viên thiết kế giao diện có thể viết CSS trực tiếp ngay trong khối HTML thành phần cho tiện quản lý, hàm xử lý CSS trong `taowebsite.py` hoạt động như sau:

1. Đọc nội dung thô của tệp component (Ví dụ: `phanchantrang.html`).
    
2. Sử dụng biểu thức chính quy (Regex) `pattern = r"<style>(.*?)</style>"` kèm cờ `re.DOTALL` để trích xuất đoạn mã CSS bên trong.
    
3. Nối đoạn mã vừa trích xuất được vào bộ đệm CSS chung toàn cục để lưu xuống `tainguyen/css/main.scss`.
    
4. Dùng `re.sub()` xóa bỏ hoàn toàn cặp thẻ `<style>...</style>` ra khỏi mã HTML gốc để trả lại mã nguồn HTML sạch bóng trước khi nhúng.
    

## IV. SẢN PHẨM ĐẦU RA MỤC TIÊU (`trangwebxuatban/`)

Thư mục kết quả sau khi trình biên dịch Python chạy xong thành công sẽ có cấu trúc thuần tĩnh 100%, sẵn sàng để triển khai lên GitHub Pages hoặc bất kỳ máy chủ lưu trữ tĩnh nào:

Plaintext

```
trangwebxuatban/
│
├── index.html               # Trang chủ hoàn chỉnh đã ráp đủ Header, Footer
├── about.html               # Trang tĩnh độc lập
├── trang-1/                 # Thư mục danh sách bài viết (Nếu bật phân trang)
│   └── index.html
│
├── lap-trinh/               # Thư mục bài viết phân theo danh mục tự động
│   └── 2026/
│       └── 07/
│           └── huong-dan-python.html
│
├── sitemap.xml             # Tệp bản đồ trang web phục vụ SEO Google
├── feed.xml                # Tệp RSS nhận tin tức tự động
└── tainguyen/               # Thư mục chứa CSS tổng hợp sạch và toàn bộ hình ảnh
    ├── css/
    │   └── main.css         # Đã được nén gọn tối đa (Compressed CSS)
    └── hinhanh/
```

