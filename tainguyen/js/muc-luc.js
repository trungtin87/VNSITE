// muc-luc.js — Tự sinh mục lục (TOC) + scroll-spy cho bài viết dài (mục IV, 🟡 nên có)
(function () {
    "use strict";
    var vung_noi_dung = document.querySelector(".noi-dung-markdown");
    var vung_muc_luc = document.getElementById("muc-luc");
    if (!vung_noi_dung || !vung_muc_luc) return;

    var cac_de_muc = vung_noi_dung.querySelectorAll("h2, h3");
    if (cac_de_muc.length < 2) {
        // Bài quá ngắn thì không cần mục lục, ẩn hẳn cho gọn giao diện
        vung_muc_luc.style.display = "none";
        return;
    }

    var ds = document.createElement("ul");
    var lien_ket_theo_id = {};

    cac_de_muc.forEach(function (de_muc, chi_so) {
        if (!de_muc.id) {
            de_muc.id = "muc-" + chi_so + "-" + de_muc.textContent
                .toLowerCase()
                .replace(/[^a-z0-9\u00C0-\u1EF9\s-]/g, "")
                .trim()
                .replace(/\s+/g, "-");
        }
        var dong = document.createElement("li");
        dong.className = de_muc.tagName === "H3" ? "cap-3" : "cap-2";
        var lien_ket = document.createElement("a");
        lien_ket.href = "#" + de_muc.id;
        lien_ket.textContent = de_muc.textContent;
        dong.appendChild(lien_ket);
        ds.appendChild(dong);
        lien_ket_theo_id[de_muc.id] = lien_ket;
    });
    vung_muc_luc.appendChild(ds);

    // Scroll-spy: highlight mục đang đọc bằng IntersectionObserver (không cần thư viện ngoài)
    if ("IntersectionObserver" in window) {
        var quan_sat = new IntersectionObserver(
            function (danh_sach_muc_tieu) {
                danh_sach_muc_tieu.forEach(function (muc_tieu) {
                    var lien_ket = lien_ket_theo_id[muc_tieu.target.id];
                    if (!lien_ket) return;
                    if (muc_tieu.isIntersecting) {
                        Object.keys(lien_ket_theo_id).forEach(function (id) {
                            lien_ket_theo_id[id].classList.remove("dang-xem");
                        });
                        lien_ket.classList.add("dang-xem");
                    }
                });
            },
            { rootMargin: "-20% 0px -70% 0px" }
        );
        cac_de_muc.forEach(function (de_muc) { quan_sat.observe(de_muc); });
    }
})();
