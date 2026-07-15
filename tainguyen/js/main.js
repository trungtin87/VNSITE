// Bùi Gia Trang — main.js
// Thuần JavaScript ES Modules. Không thư viện ngoài.
import { searchIndex } from "./search-data.js";

const THEME_KEY = "hktq-theme";

/* ---------------- Âm / Dương — chuyển giao diện sáng-tối ---------------- */
function initTheme() {
  const root = document.documentElement;
  const stored = localStorage.getItem(THEME_KEY);
  if (stored) root.setAttribute("data-theme", stored);

  const toggle = document.querySelector("[data-theme-toggle]");
  if (!toggle) return;

  toggle.addEventListener("click", () => {
    const current =
      root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem(THEME_KEY, next);
  });
}

/* ---------------- Menu di động ---------------- */
function initMobileNav() {
  const btn = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (!btn || !nav) return;

  const closeNav = () => {
    nav.classList.remove("is-open");
    btn.setAttribute("aria-expanded", "false");
  };

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", String(isOpen));
  });

  nav.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", closeNav)
  );

  // Bấm ra ngoài menu (nền/overlay) thì đóng lại
  document.addEventListener("click", (e) => {
    if (!nav.classList.contains("is-open")) return;
    if (nav.contains(e.target) || btn.contains(e.target)) return;
    closeNav();
  });

  // Nhấn phím Esc để đóng
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      closeNav();
      btn.focus();
    }
  });
}

/* ---------------- Highlight mục menu hiện tại ---------------- */
function highlightActiveMenu() {
  const path = window.location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".nav-list a").forEach((a) => {
    const href = a.getAttribute("href");
    if (!href) return;
    const normalized = href.replace(/index\.html$/, "");
    if (normalized === path || (normalized !== "/" && path.startsWith(normalized))) {
      a.setAttribute("aria-current", "page");
    }
  });
}

/* ---------------- Về đầu trang ---------------- */
function initBackToTop() {
  const btn = document.querySelector("[data-back-to-top]");
  if (!btn) return;
  const onScroll = () => {
    btn.classList.toggle("is-visible", window.scrollY > 640);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

/* ---------------- Tìm kiếm bài viết ---------------- */
function initSearch() {
  const openBtn = document.querySelector("[data-search-open]");
  const panel = document.querySelector("[data-search-panel]");
  if (!openBtn || !panel) return;
  const input = panel.querySelector("[data-search-input]");
  const results = panel.querySelector("[data-search-results]");

  const render = (query) => {
    const q = query.trim().toLowerCase();
    if (!q) {
      results.innerHTML = "";
      return;
    }
    const matches = searchIndex.filter((item) =>
      [item.title, item.desc, item.category].join(" ").toLowerCase().includes(q)
    );
    if (matches.length === 0) {
      results.innerHTML = `<li class="search-empty">Không tìm thấy bài viết phù hợp.</li>`;
      return;
    }
    results.innerHTML = matches
      .map(
        (item) => `
        <li><a href="${item.url}">
          <span class="r-cat">${item.category}</span><br>
          ${item.title}
        </a></li>`
      )
      .join("");
  };

  const open = () => {
    panel.classList.add("is-open");
    input.value = "";
    results.innerHTML = "";
    input.focus();
    document.addEventListener("keydown", onKeydown);
  };
  const close = () => {
    panel.classList.remove("is-open");
    document.removeEventListener("keydown", onKeydown);
    openBtn.focus();
  };
  const onKeydown = (e) => {
    if (e.key === "Escape") close();
  };

  openBtn.addEventListener("click", open);
  panel.addEventListener("click", (e) => {
    if (e.target === panel) close();
  });
  panel.querySelector("[data-search-close]")?.addEventListener("click", close);
  input?.addEventListener("input", (e) => render(e.target.value));

  document.addEventListener("keydown", (e) => {
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      open();
    }
  });
}

/* ---------------- Mục lục tự động cho bài viết ---------------- */
function initTableOfContents() {
  const body = document.querySelector("[data-post-body]");
  const tocContainer = document.querySelector("[data-toc-list]");
  if (!body || !tocContainer) return;

  const headings = Array.from(body.querySelectorAll("h2, h3"));
  if (headings.length === 0) {
    document.querySelector("[data-toc]")?.setAttribute("hidden", "");
    return;
  }

  const slugCount = {};
  const items = headings.map((h) => {
    let slug =
      h.id ||
      h.textContent
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "");
    if (slugCount[slug] != null) {
      slugCount[slug] += 1;
      slug = `${slug}-${slugCount[slug]}`;
    } else {
      slugCount[slug] = 0;
    }
    h.id = slug;
    return { slug, text: h.textContent, level: h.tagName };
  });

  let html = "<ol>";
  let openSub = false;
  items.forEach((item) => {
    if (item.level === "H3") {
      if (!openSub) {
        html += "<ol>";
        openSub = true;
      }
      html += `<li><a href="#${item.slug}">${item.text}</a></li>`;
    } else {
      if (openSub) {
        html += "</ol>";
        openSub = false;
      }
      html += `<li><a href="#${item.slug}">${item.text}</a></li>`;
    }
  });
  if (openSub) html += "</ol>";
  html += "</ol>";
  tocContainer.innerHTML = html;

  const tocLinks = tocContainer.querySelectorAll("a");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        tocLinks.forEach((a) => a.classList.remove("is-active"));
        const link = tocContainer.querySelector(`a[href="#${entry.target.id}"]`);
        link?.classList.add("is-active");
      });
    },
    { rootMargin: "-20% 0px -70% 0px" }
  );
  headings.forEach((h) => observer.observe(h));
}

/* ---------------- Thời gian đọc ---------------- */
function initReadingTime() {
  const body = document.querySelector("[data-post-body]");
  const out = document.querySelector("[data-reading-time]");
  if (!body || !out) return;
  const words = body.textContent.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.round(words / 200));
  out.textContent = `${minutes} phút đọc`;
}

/* ---------------- Sao chép liên kết bài viết ---------------- */
function initCopyLink() {
  const btn = document.querySelector("[data-copy-link]");
  if (!btn) return;
  const label = btn.querySelector("[data-copy-label]");
  const defaultText = label ? label.textContent : btn.textContent;
  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
    } catch {
      const t = document.createElement("textarea");
      t.value = window.location.href;
      document.body.appendChild(t);
      t.select();
      document.execCommand("copy");
      t.remove();
    }
    if (label) {
      label.textContent = "Đã sao chép";
      setTimeout(() => (label.textContent = defaultText), 1800);
    }
  });
}

/* ---------------- Bộ lọc thư viện ---------------- */
function initLibraryFilter() {
  const tabs = document.querySelectorAll("[data-lib-tab]");
  const items = document.querySelectorAll("[data-lib-item]");
  if (tabs.length === 0) return;
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const kind = tab.getAttribute("data-lib-tab");
      tabs.forEach((t) => t.setAttribute("aria-pressed", "false"));
      tab.setAttribute("aria-pressed", "true");
      items.forEach((item) => {
        const show = kind === "all" || item.getAttribute("data-lib-item") === kind;
        item.hidden = !show;
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initMobileNav();
  highlightActiveMenu();
  initBackToTop();
  initSearch();
  initTableOfContents();
  initReadingTime();
  initCopyLink();
  initLibraryFilter();
});
