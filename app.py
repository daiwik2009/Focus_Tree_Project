from pathlib import Path
from urllib.request import Request, urlopen

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for
from flask_wtf.csrf import CSRFProtect

from db import (
    SCOPE_COPY,
    SCOPES,
    add_focus,
    delete_focus,
    get_db,
    get_focus,
    get_icon,
    icon_categories,
    icon_count,
    init_db,
    list_focuses,
    replace_icons,
    score_totals,
    search_icons,
    set_completed,
)
from forms import FocusForm
from scraper import scrape_icons

app = Flask(__name__)
app.config["SECRET_KEY"] = "life-focus-tree-local-secret"
csrf = CSRFProtect(app)
ICON_CACHE = Path(__file__).resolve().parent / "data" / "icon_cache"


def ensure_icons(conn):
    if icon_count(conn) > 0:
        return
    try:
        replace_icons(conn, scrape_icons())
    except Exception as exc:
        app.logger.warning("Icon scrape skipped: %s", exc)


def parent_choices(focuses):
    return [(0, "None (root focus)")] + [
        (f["id"], f["name"]) for f in focuses if not f["completed"]
    ] + [
        (f["id"], f"{f['name']} (done)")
        for f in focuses
        if f["completed"]
    ]


def is_available(focus, by_id):
    if focus["completed"]:
        return False
    parent_id = focus["parent_id"]
    if not parent_id:
        return True
    parent = by_id.get(parent_id)
    return bool(parent and parent["completed"])


def decorate_focuses(focuses):
    by_id = {f["id"]: f for f in focuses}
    decorated = []
    for focus in focuses:
        item = dict(focus)
        item["available"] = is_available(focus, by_id)
        parent = by_id.get(focus["parent_id"]) if focus["parent_id"] else None
        item["parent_name"] = parent["name"] if parent else None
        item["locked"] = not item["available"] and not item["completed"]
        decorated.append(item)
    return decorated


@app.before_request
def setup():
    init_db()


@app.route("/")
def index():
    scope = request.args.get("scope", "yearly")
    if scope not in SCOPES:
        scope = "yearly"

    with get_db() as conn:
        ensure_icons(conn)
        focuses = decorate_focuses(list_focuses(conn, scope))
        overall, by_scope = score_totals(conn)
        categories = icon_categories(conn)

    form = FocusForm(scope=scope)
    form.parent_id.choices = parent_choices(focuses)

    active = [f for f in focuses if f["available"]]
    return render_template(
        "index.html",
        form=form,
        scope=scope,
        scopes=SCOPES,
        scope_copy=SCOPE_COPY,
        focuses=focuses,
        active_focuses=active,
        overall=overall,
        by_scope=by_scope,
        icon_categories=categories,
    )


@app.post("/add-focus")
def create_focus():
    form = FocusForm()
    scope = form.scope.data if form.scope.data in SCOPES else "yearly"

    with get_db() as conn:
        focuses = list_focuses(conn, scope)
        form.parent_id.choices = parent_choices(focuses)
        if not form.validate_on_submit():
            overall, by_scope = score_totals(conn)
            categories = icon_categories(conn)
            decorated = decorate_focuses(focuses)
            return render_template(
                "index.html",
                form=form,
                scope=scope,
                scopes=SCOPES,
                scope_copy=SCOPE_COPY,
                focuses=decorated,
                active_focuses=[f for f in decorated if f["available"]],
                overall=overall,
                by_scope=by_scope,
                icon_categories=categories,
            ), 400

        parent_id = form.parent_id.data or 0
        if parent_id:
            parent = get_focus(conn, parent_id)
            if not parent or parent["scope"] != scope:
                parent_id = None
        else:
            parent_id = None

        add_focus(
            conn,
            scope=scope,
            name=form.name.data,
            description=form.description.data,
            completion_time=form.completion_time.data,
            points=form.points.data,
            icon=form.icon.data,
            parent_id=parent_id,
        )

    return redirect(url_for("index", scope=scope))


@app.post("/focus/<int:focus_id>/complete")
def complete_focus(focus_id):
    with get_db() as conn:
        focus = get_focus(conn, focus_id)
        if not focus:
            return redirect(url_for("index"))
        siblings = decorate_focuses(list_focuses(conn, focus["scope"]))
        current = next(f for f in siblings if f["id"] == focus_id)
        if current["available"]:
            set_completed(conn, focus_id, True)
        return redirect(url_for("index", scope=focus["scope"]))


@app.post("/focus/<int:focus_id>/uncomplete")
def uncomplete_focus(focus_id):
    with get_db() as conn:
        focus = get_focus(conn, focus_id)
        if not focus:
            return redirect(url_for("index"))
        children = conn.execute(
            "SELECT id FROM focuses WHERE parent_id = ? AND completed = 1",
            (focus_id,),
        ).fetchall()
        if not children:
            set_completed(conn, focus_id, False)
        return redirect(url_for("index", scope=focus["scope"]))


@app.post("/focus/<int:focus_id>/delete")
def remove_focus(focus_id):
    with get_db() as conn:
        focus = get_focus(conn, focus_id)
        if not focus:
            return redirect(url_for("index"))
        delete_focus(conn, focus_id)
        return redirect(url_for("index", scope=focus["scope"]))


@app.get("/api/icons")
def api_icons():
    query = request.args.get("q", "")
    category = request.args.get("category", "National focuses")
    page = max(int(request.args.get("page", 1)), 1)
    limit = 72
    offset = (page - 1) * limit
    with get_db() as conn:
        ensure_icons(conn)
        icons, total = search_icons(
            conn, query=query, category=category, limit=limit, offset=offset
        )
    for icon in icons:
        icon["src"] = url_for("gfx", icon_id=icon["id"])
    return jsonify(
        {
            "icons": icons,
            "total": total,
            "page": page,
            "pages": max((total + limit - 1) // limit, 1),
        }
    )


@app.get("/gfx/<int:icon_id>")
def gfx(icon_id):
    with get_db() as conn:
        icon = get_icon(conn, icon_id)
    if not icon:
        abort(404)
    ICON_CACHE.mkdir(parents=True, exist_ok=True)
    dest = ICON_CACHE / f"{icon_id}.png"
    if not dest.exists():
        request_remote = Request(
            icon["url"],
            headers={"User-Agent": "FocusTreeLifeGoals/1.0"},
        )
        with urlopen(request_remote, timeout=20) as response:
            dest.write_bytes(response.read())
    return send_file(dest, mimetype="image/png")


@app.post("/api/icons/refresh")
def refresh_icons():
    with get_db() as conn:
        replace_icons(conn, scrape_icons())
        return jsonify({"ok": True, "count": icon_count(conn)})


if __name__ == "__main__":
    init_db()
    with get_db() as conn:
        ensure_icons(conn)
    app.run(debug=True)
