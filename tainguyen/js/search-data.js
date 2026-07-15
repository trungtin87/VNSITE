// Chỉ mục tìm kiếm — được SINH TỰ ĐỘNG mỗi lần chạy `python taowebsite.py build`
// (xem hàm _sinh_chi_muc_tim_kiem trong vnsite_engine/builder.py).
// KHÔNG chỉnh tay tệp này — mọi thay đổi sẽ bị ghi đè ở lần build kế tiếp;
// hãy sửa front matter của bài viết trong _cacbaiviet/ rồi build lại.
export const searchIndex = [
  {
    title: "Vô vi trong tối ưu hệ thống",
    url: "/ky-thuat/2026/06/vo-vi-va-toi-uu/",
    category: "Kỹ thuật",
    desc: "Tối ưu bằng cách bớt đi, không phải thêm vào — ghi chú từ việc dọn dẹp một hệ thống chạy quá nhiều tiến trình không cần thiết.",
  },
  {
    title: "Âm — Dương trong kiến trúc phần mềm",
    url: "/ky-thuat/2026/06/am-duong-trong-lap-trinh/",
    category: "Kỹ thuật",
    desc: "Đối lập nhưng bổ sung — đồng bộ và bất đồng bộ, trạng thái và bất biến, đơn giản và đầy đủ.",
  },
  {
    title: "Đạo pháp tự nhiên — khi lập trình học theo dòng nước",
    url: "/triet-hoc/2026/06/dao-phap-tu-nhien/",
    category: "Triết học",
    desc: "Tại sao những hệ thống bền vững nhất thường là những hệ thống ít can thiệp nhất, và điều đó nói gì với người viết phần mềm.",
  }
];
