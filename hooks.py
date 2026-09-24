from pathlib import Path
from datetime import datetime, date
import yaml

from pathlib import Path
import yaml

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

def on_page_markdown(markdown, page, config, files):

    slug = Path(page.file.src_uri).stem

    album = load_gallery_album(
        config,
        slug
    )

    if not album:
        return markdown

    page.meta["template"] = "gallery-album.html"

    page.meta["hide"] = [
        "navigation",
        "toc"
    ]

    page.meta["album"] = album

    return ""

def on_page_context(
    context,
    page,
    config,
    nav
):

    if page.file.src_uri == "index.md":

        context["latest_news"] = (
            load_news(config)[:3]
        )


    if page.file.src_uri == "galeria/index.md":

        context["gallery_albums"] = (
            load_gallery(config)
        )


    if page.file.src_uri == "videos/index.md":

        context["videos"] = (
            load_videos(config)
        )


    return context

def load_gallery(config):

    docs_dir = Path(config["docs_dir"])

    albums_dir = (
        docs_dir
        / "galeria"
        / "albums"
    )

    albums = []

    if not albums_dir.exists():
        return albums

    for album_dir in albums_dir.iterdir():

        if not album_dir.is_dir():
            continue

        info_file = album_dir / "info.yml"

        if not info_file.exists():
            continue

        try:
            metadata = yaml.safe_load(
                info_file.read_text(
                    encoding="utf-8"
                )
            ) or {}
        except Exception as e:

            print(
                f"[GALERIA] Error leyendo "
                f"{info_file}: {e}"
            )

            continue

        title = metadata.get(
            "title",
            album_dir.name
        )

        images = sorted([
            file
            for file in album_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ])

        if not images:
            continue

        cover = images[0]

        albums.append({
            "title": title,
            "date": metadata.get("date", ""),
            "description": metadata.get(
                "description",
                ""
            ),
            "slug": album_dir.name,
            "count": len(images),
            "cover": (
                f"galeria/albums/"
                f"{album_dir.name}/"
                f"{cover.name}"
            ),
            "url": (
                f"galeria/"
                f"{album_dir.name}/"
            ),
        })

    albums.sort(
        key=lambda item: (
            str(item["date"]),
            item["title"]
        ),
        reverse=True
    )

    return albums

def load_gallery_album(config, slug):

    docs_dir = Path(config["docs_dir"])

    album_dir = (
        docs_dir
        / "galeria"
        / "albums"
        / slug
    )

    info_file = album_dir / "info.yml"

    if not album_dir.exists():
        return None

    metadata = {}

    if info_file.exists():
        metadata = yaml.safe_load(
            info_file.read_text(encoding="utf-8")
        ) or {}

    images = sorted([
        file
        for file in album_dir.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ])

    return {
        "title": metadata.get("title", slug),
        "date": metadata.get("date", ""),
        "description": metadata.get("description", ""),
        "slug": slug,

        "images": [
            f"galeria/albums/{slug}/{file.name}"
            for file in images
        ]
    }

def load_news(config):

    posts_dir = (
        Path(config["docs_dir"])
        / "noticias"
        / "posts"
    )

    if not posts_dir.exists():
        print("[NOTICIAS] ERROR: la carpeta no existe")
        return []

    news = []

    for file in posts_dir.glob("*.md"):

        text = file.read_text(encoding="utf-8")

        # Debe comenzar por front matter YAML
        if not text.startswith("---"):
            print(f"[NOTICIAS] {file.name}: no tiene front matter")
            continue

        parts = text.split("---", 2)

        if len(parts) < 3:
            print(f"[NOTICIAS] {file.name}: front matter incorrecto")
            continue

        try:
            metadata = yaml.safe_load(parts[1]) or {}
        except Exception as e:
            print(f"[NOTICIAS] {file.name}: error YAML: {e}")
            continue

        title = metadata.get("title")
        news_date = metadata.get("date")

        if not title:
            print(f"[NOTICIAS] {file.name}: falta title")
            continue

        if not news_date:
            print(f"[NOTICIAS] {file.name}: falta date")
            continue

        # YAML normalmente convierte 2026-09-24 directamente a date
        if isinstance(news_date, str):
            try:
                news_date = datetime.strptime(
                    news_date,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                print(
                    f"[NOTICIAS] {file.name}: "
                    f"fecha incorrecta: {news_date}"
                )
                continue

        slug = lug = metadata.get("slug", file.stem)

        news.append({
            "title": title,
            "date": news_date,
            "description": metadata.get("description", ""),
            "image": metadata.get("image", ""),
            "url": f"noticias/{slug}/",
        })

    news.sort(
        key=lambda item: item["date"],
        reverse=True
    )

    return news

def load_videos(config):

    docs_dir = Path(config["docs_dir"])

    videos_file = (
        docs_dir
        / "videos"
        / "videos.yml"
    )

    if not videos_file.exists():
        return []

    try:
        videos = yaml.safe_load(
            videos_file.read_text(
                encoding="utf-8"
            )
        ) or []

    except Exception as e:

        print(
            f"[VIDEOS] Error leyendo videos.yml: {e}"
        )

        return []

    return videos