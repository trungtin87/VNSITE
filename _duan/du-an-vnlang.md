---
tieu_de: "VNLang"
mo_ta_ngan: "Ngôn ngữ lập trình dùng từ khóa tiếng Việt, kèm bộ công cụ biên dịch đầy đủ."
anh_dai_dien: "/tainguyen/hinhanh/du-an-vnlang.png"
cong_nghe: [Python, "Trình biên dịch", "Đa nền tảng đích"]
link_demo: ""
link_github: "https://github.com/tenban/vnlang"
---

VNLang là một ngôn ngữ lập trình thử nghiệm cho phép viết mã bằng từ khóa
tiếng Việt (`nếu`, `khi`, `hàm`...), với bộ công cụ biên dịch đầy đủ: lexer,
parser, resolver, type checker và codegen nhắm tới nhiều backend (Python,
JavaScript, và các backend đang phát triển như Rust, Go, Kotlin, Swift).

Dự án còn bao gồm một tầng thông dịch tự lưu trữ (self-hosted interpreter)
được viết bằng chính VNLang, cùng bộ test conformance đảm bảo mọi backend
đều tuân theo cùng một đặc tả ngôn ngữ (EBNF).
