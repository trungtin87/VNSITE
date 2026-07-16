// sao-chep-code.js — Thêm nút "Sao chép" cho mỗi khối <pre><code> (mục IV, 🟡 nên có)
(function () {
    "use strict";
    var cac_khoi_pre = document.querySelectorAll(".noi-dung-markdown pre");

    cac_khoi_pre.forEach(function (khoi_pre) {
        var nut = document.createElement("button");
        nut.type = "button";
        nut.className = "nut-sao-chep-code";
        nut.textContent = "Sao chép";
        khoi_pre.appendChild(nut);

        nut.addEventListener("click", function () {
            var noi_dung_code = khoi_pre.querySelector("code");
            var van_ban = noi_dung_code ? noi_dung_code.textContent : khoi_pre.textContent;

            var xong = function () {
                nut.textContent = "Đã sao chép ✓";
                setTimeout(function () { nut.textContent = "Sao chép"; }, 1600);
            };

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(van_ban).then(xong, function () {
                    nut.textContent = "Lỗi sao chép";
                });
            } else {
                // Phương án dự phòng cho trình duyệt cũ không có Clipboard API
                var vung_tam = document.createElement("textarea");
                vung_tam.value = van_ban;
                vung_tam.style.position = "fixed";
                vung_tam.style.opacity = "0";
                document.body.appendChild(vung_tam);
                vung_tam.select();
                try { document.execCommand("copy"); xong(); } catch (loi) { nut.textContent = "Lỗi sao chép"; }
                document.body.removeChild(vung_tam);
            }
        });
    });
})();
