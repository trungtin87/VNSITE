---
tieu_de: "Tại sao chọn Python làm công cụ tạo web tĩnh"
chuyen_muc: "lap-trinh"
tags: [python, static-site, kien-truc]
mo_ta: "Lý do VNSITE chọn Python thuần thay vì phụ thuộc vào hệ sinh thái Node.js."
---

Có rất nhiều trình tạo website tĩnh trên thị trường: Jekyll (Ruby), Hugo (Go),
Next.js/Gatsby (Node.js)... Vậy tại sao VNSITE lại chọn Python?

<!--tomtat-->

## 1. Đơn giản hóa môi trường cài đặt

Phần lớn máy tính hoặc môi trường CI hiện nay đã có sẵn Python 3. Người dùng
không cần cài thêm Ruby, Node.js hay quản lý `node_modules` cồng kềnh.

## 2. Dễ tùy biến cho người không chuyên lập trình

Cú pháp template thuần tiếng Việt giúp người viết blog không rành lập trình
vẫn có thể đọc hiểu và chỉnh sửa layout của chính mình.

## 3. Một hệ sinh thái, một ngôn ngữ

Từ bộ máy build, plugin, cho tới các script phụ trợ (sinh favicon, gộp CSS),
tất cả đều là Python — dễ bảo trì hơn nhiều so với việc trộn nhiều ngôn ngữ.
