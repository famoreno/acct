from pathlib import Path

import mkdocs_gen_files
import yaml


DOCS_DIR = Path("docs")

ALBUMS_DIR = (
    DOCS_DIR
    / "galeria"
    / "albums"
)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


if ALBUMS_DIR.exists():

    for album_dir in sorted(ALBUMS_DIR.iterdir()):

        if not album_dir.is_dir():
            continue

        info_file = album_dir / "info.yml"

        if not info_file.exists():
            continue

        metadata = yaml.safe_load(
            info_file.read_text(
                encoding="utf-8"
            )
        ) or {}

        images = sorted([
            file.name
            for file in album_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ])

        if not images:
            continue

        slug = album_dir.name

        page_meta = {
            "template": "gallery-album.html",

            "hide": [
                "navigation",
                "toc"
            ],

            "title": metadata.get(
                "title",
                slug
            ),

            "album_date": metadata.get(
                "date",
                ""
            ),

            "description": metadata.get(
                "description",
                ""
            ),

            "album_slug": slug,

            "images": images,
        }

        output_path = (
            Path("galeria")
            / f"{slug}.md"
        )

        with mkdocs_gen_files.open(
            output_path,
            "w"
        ) as f:

            f.write("---\n")

            f.write(
                yaml.safe_dump(
                    page_meta,
                    allow_unicode=True,
                    sort_keys=False
                )
            )

            f.write("---\n")