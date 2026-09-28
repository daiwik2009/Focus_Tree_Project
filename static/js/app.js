(function () {
    const dataEl = document.getElementById("focus-data");
    const tree = document.getElementById("tree-canvas");
    const lines = document.getElementById("tree-lines");
    const overlay = document.getElementById("detail-overlay");
    const picker = document.getElementById("picker-overlay");
    const focuses = dataEl ? JSON.parse(dataEl.textContent) : [];

    function closeAll() {
        overlay.classList.remove("open");
        picker.classList.remove("open");
    }

    document.querySelectorAll("[data-close]").forEach((btn) => {
        btn.addEventListener("click", closeAll);
    });
    [overlay, picker].forEach((el) => {
        el.addEventListener("click", (e) => {
            if (e.target === el) closeAll();
        });
    });

    if (tree && lines && focuses.length) {
        const COL = 250;
        const ROW = 150;
        const NODE_W = 228;
        const NODE_H = 118;

        function layout(nodes) {
            const byParent = new Map();
            nodes.forEach((n) => {
                const key = n.parent_id || 0;
                if (!byParent.has(key)) byParent.set(key, []);
                byParent.get(key).push(n);
            });
            const pos = {};
            let yCursor = 0;

            function walk(node, depth) {
                const children = byParent.get(node.id) || [];
                if (!children.length) {
                    pos[node.id] = { x: depth, y: yCursor };
                    yCursor += 1;
                    return pos[node.id].y;
                }
                const ys = children.map((child) => walk(child, depth + 1));
                const mid = (Math.min(...ys) + Math.max(...ys)) / 2;
                pos[node.id] = { x: depth, y: mid };
                return mid;
            }

            const ids = new Set(nodes.map((n) => n.id));
            const roots = nodes.filter((n) => !n.parent_id || !ids.has(n.parent_id));
            roots.forEach((root, i) => {
                walk(root, 0);
                if (i < roots.length - 1) yCursor += 0.35;
            });
            return pos;
        }

        const positions = layout(focuses);
        let maxX = 0;
        let maxY = 0;
        Object.values(positions).forEach((p) => {
            maxX = Math.max(maxX, p.x);
            maxY = Math.max(maxY, p.y);
        });
        tree.style.width = `${Math.max((maxX + 1) * COL + 40, 400)}px`;
        tree.style.height = `${Math.max((maxY + 1) * ROW + 40, 360)}px`;

        focuses.forEach((focus) => {
            const p = positions[focus.id];
            if (!p) return;
            const el = document.createElement("button");
            el.type = "button";
            el.className = "focus-node";
            if (focus.completed) el.classList.add("completed");
            else if (focus.available) el.classList.add("available");
            else el.classList.add("locked");
            el.style.left = `${p.x * COL}px`;
            el.style.top = `${p.y * ROW}px`;
            const icon = focus.icon
                ? `<img src="${focus.icon}" alt="">`
                : "<span>?</span>";
            el.innerHTML = `
                <div class="focus-icon">${icon}</div>
                <div class="focus-name"></div>
                <div class="focus-points"></div>
            `;
            el.querySelector(".focus-name").textContent = focus.name;
            el.querySelector(".focus-points").textContent = `${focus.points} PP`;
            el.addEventListener("click", () => openDetail(focus));
            tree.appendChild(el);
        });

        const svgNS = "http://www.w3.org/2000/svg";
        lines.setAttribute("width", tree.style.width);
        lines.setAttribute("height", tree.style.height);
        const byId = Object.fromEntries(focuses.map((f) => [f.id, f]));
        focuses.forEach((focus) => {
            if (!focus.parent_id || !positions[focus.id] || !positions[focus.parent_id]) return;
            const a = positions[focus.parent_id];
            const b = positions[focus.id];
            const x1 = a.x * COL + NODE_W;
            const y1 = a.y * ROW + NODE_H / 2;
            const x2 = b.x * COL;
            const y2 = b.y * ROW + NODE_H / 2;
            const path = document.createElementNS(svgNS, "path");
            const mid = (x1 + x2) / 2;
            path.setAttribute("d", `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`);
            path.setAttribute("fill", "none");
            path.setAttribute("stroke", byId[focus.parent_id].completed ? "#d4b56a" : "rgba(255,255,255,0.28)");
            path.setAttribute("stroke-width", "2");
            lines.appendChild(path);
        });
    }

    function openDetail(focus) {
        document.getElementById("detail-name").textContent = focus.name;
        document.getElementById("detail-desc").textContent =
            focus.description || "No briefing written for this focus yet.";
        document.getElementById("detail-points").textContent = `${focus.points} political power`;
        document.getElementById("detail-time").textContent = focus.completion_time || "Unspecified";
        document.getElementById("detail-status").textContent = focus.completed
            ? "Completed"
            : focus.available
              ? "Available"
              : "Locked";
        document.getElementById("detail-prereq").textContent = focus.parent_name || "None";
        const img = document.getElementById("detail-img");
        if (focus.icon) {
            img.src = focus.icon;
            img.style.display = "block";
        } else {
            img.removeAttribute("src");
            img.style.display = "none";
        }
        const completeForm = document.getElementById("complete-form");
        const undoForm = document.getElementById("undo-form");
        const deleteForm = document.getElementById("delete-form");
        completeForm.action = `/focus/${focus.id}/complete`;
        undoForm.action = `/focus/${focus.id}/uncomplete`;
        deleteForm.action = `/focus/${focus.id}/delete`;
        completeForm.style.display = focus.available ? "inline" : "none";
        undoForm.style.display = focus.completed ? "inline" : "none";
        overlay.classList.add("open");
    }

    const iconInput = document.getElementById("icon-input");
    const iconPreview = document.getElementById("icon-preview");
    if (iconInput && iconInput.value && iconPreview) {
        iconPreview.src = iconInput.value;
        iconPreview.style.display = "inline";
    }
    const openPicker = document.getElementById("open-picker");
    const iconGrid = document.getElementById("icon-grid");
    const iconSearch = document.getElementById("icon-search");
    const iconCategory = document.getElementById("icon-category");
    const pageLabel = document.getElementById("page-label");
    const prevPage = document.getElementById("prev-page");
    const nextPage = document.getElementById("next-page");
    const refreshIcons = document.getElementById("refresh-icons");
    let page = 1;

    async function loadIcons() {
        const params = new URLSearchParams({
            q: iconSearch.value,
            category: iconCategory.value,
            page: String(page),
        });
        const res = await fetch(`/api/icons?${params.toString()}`);
        const data = await res.json();
        iconGrid.innerHTML = "";
        data.icons.forEach((icon) => {
            const cell = document.createElement("button");
            cell.type = "button";
            cell.className = "icon-cell";
            cell.innerHTML = `<img alt=""><span></span>`;
            const src = icon.src || `/gfx/${icon.id}`;
            cell.querySelector("img").src = src;
            cell.querySelector("span").textContent = icon.name;
            cell.addEventListener("click", () => {
                iconInput.value = src;
                iconPreview.src = src;
                iconPreview.style.display = "inline";
                closeAll();
            });
            iconGrid.appendChild(cell);
        });
        pageLabel.textContent = `Page ${data.page} / ${data.pages} · ${data.total} icons`;
        prevPage.disabled = data.page <= 1;
        nextPage.disabled = data.page >= data.pages;
    }

    openPicker.addEventListener("click", () => {
        picker.classList.add("open");
        page = 1;
        loadIcons();
    });
    iconSearch.addEventListener("input", () => {
        page = 1;
        loadIcons();
    });
    iconCategory.addEventListener("change", () => {
        page = 1;
        loadIcons();
    });
    prevPage.addEventListener("click", () => {
        page = Math.max(1, page - 1);
        loadIcons();
    });
    nextPage.addEventListener("click", () => {
        page += 1;
        loadIcons();
    });
    refreshIcons.addEventListener("click", async () => {
        refreshIcons.textContent = "Scraping…";
        const token = document.querySelector('meta[name="csrf-token"]').content;
        await fetch("/api/icons/refresh", {
            method: "POST",
            headers: { "X-CSRFToken": token },
        });
        refreshIcons.textContent = "Rescrape icons";
        page = 1;
        loadIcons();
    });
})();
