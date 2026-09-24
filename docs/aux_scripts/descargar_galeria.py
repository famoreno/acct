import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, NavigableString, Tag


URL = "https://gtloscriticos.wordpress.com/2024/05/16/galeria/"

OUTPUT_DIR = Path("docs/galeria/albums")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def slugify(text):

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = text.encode(
        "ascii",
        "ignore"
    ).decode("ascii")

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    return text.strip("-")


def clean_wordpress_url(url):

    url = url.split("?")[0]

    url = re.sub(
        r"-\d+x\d+(?=\.(jpg|jpeg|png|webp)$)",
        "",
        url,
        flags=re.IGNORECASE,
    )

    return url


def get_best_image_url(img):

    # WordPress suele incluir la URL original aquí
    url = img.get("data-orig-file")

    if url:
        return clean_wordpress_url(
            urljoin(URL, url)
        )

    # Si no, buscamos la mayor de srcset
    srcset = img.get("srcset")

    if srcset:

        candidates = []

        for item in srcset.split(","):

            parts = item.strip().split()

            if not parts:
                continue

            candidate_url = parts[0]

            width = 0

            if len(parts) > 1:

                try:
                    width = int(
                        parts[1].replace(
                            "w",
                            ""
                        )
                    )

                except ValueError:
                    pass

            candidates.append(
                (
                    width,
                    candidate_url
                )
            )

        if candidates:

            _, candidate_url = max(
                candidates,
                key=lambda x: x[0]
            )

            return clean_wordpress_url(
                urljoin(
                    URL,
                    candidate_url
                )
            )

    src = img.get("src")

    if not src:
        return None

    return clean_wordpress_url(
        urljoin(
            URL,
            src
        )
    )


def is_image_url(url):

    if not url:
        return False

    path = urlparse(url).path.lower()

    return any(
        path.endswith(ext)
        for ext in IMAGE_EXTENSIONS
    )


def is_album_title(text):
    """
    Detecta las etiquetas/títulos usados realmente
    en esta página de WordPress.
    """

    text = " ".join(
        text.split()
    ).strip()

    if not text:
        return False

    upper = text.upper()

    # Títulos concretos que aparecen en la web
    if upper.startswith(
        "ULTIMAS COLABORACIONES"
    ):
        return True

    if upper.startswith(
        "ÚLTIMAS COLABORACIONES"
    ):
        return True

    if upper.startswith(
        "OBRA DE TEATRO"
    ):
        return True

    return False


def extract_albums(soup):

    content = (
        soup.select_one(".entry-content")
        or soup.select_one(".post-content")
        or soup.select_one("article")
    )

    if content is None:
        print("No encuentro el contenido principal del post.")
        return []

    albums = []
    current_album = None

    seen_images = set()

    # Imágenes encontradas antes del primer título
    pending_images = []

    for node in content.descendants:

        # ---------------------------------------------
        # TEXTO
        # ---------------------------------------------

        if isinstance(node, NavigableString):

            parent = node.parent

            if (
                parent
                and parent.name in {
                    "script",
                    "style"
                }
            ):
                continue

            text = str(node).strip()

            if not is_album_title(text):
                continue

            title = " ".join(
                text.split()
            )

            print(
                f"[TÍTULO] {title}"
            )

            # Caso especial:
            # el título de "Últimas colaboraciones con ONG"
            # aparece DESPUÉS de sus imágenes
            if (
                title.upper().startswith(
                    "ULTIMAS COLABORACIONES"
                )
                or title.upper().startswith(
                    "ÚLTIMAS COLABORACIONES"
                )
            ):

                current_album = {
                    "title": title,
                    "images": pending_images.copy()
                }

                albums.append(
                    current_album
                )

                print(
                    f"  -> asignadas "
                    f"{len(pending_images)} imágenes previas"
                )

                pending_images.clear()

            else:

                # Para el resto de álbumes,
                # el título aparece antes de las imágenes
                current_album = {
                    "title": title,
                    "images": []
                }

                albums.append(
                    current_album
                )

        # ---------------------------------------------
        # IMAGEN
        # ---------------------------------------------

        elif (
            isinstance(node, Tag)
            and node.name == "img"
        ):

            image_url = get_best_image_url(
                node
            )

            if not is_image_url(
                image_url
            ):
                continue

            if image_url in seen_images:
                continue

            seen_images.add(
                image_url
            )

            # Antes de haber encontrado ningún título:
            # acumulamos imágenes
            if current_album is None:

                pending_images.append(
                    image_url
                )

            else:

                current_album[
                    "images"
                ].append(
                    image_url
                )

    albums = [
        album
        for album in albums
        if album["images"]
    ]

    return albums


def download_image(
    url,
    destination
):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        if not response.headers.get(
            "Content-Type",
            ""
        ).startswith("image/"):

            print(
                f"  [IGNORADA] {url}"
            )

            return False

        destination.write_bytes(
            response.content
        )

        return True

    except Exception as e:

        print(
            f"  [ERROR] {url}"
        )

        print(
            f"          {e}"
        )

        return False


def create_album(album):

    title = album["title"]

    # Limpieza de nombres para que queden más bonitos
    pretty_title = re.sub(
        r"^OBRA DE TEATRO\s+",
        "",
        title,
        flags=re.IGNORECASE
    )

    pretty_title = re.sub(
        r"^ULTIMAS COLABORACIONES CON ONG$",
        "Últimas colaboraciones con ONG",
        pretty_title,
        flags=re.IGNORECASE
    )

    slug = slugify(
        pretty_title
    )

    album_dir = (
        OUTPUT_DIR
        / slug
    )

    album_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print(
        f"[ÁLBUM] {pretty_title}"
    )

    print(
        f"        {len(album['images'])} imágenes"
    )

    info_file = (
        album_dir
        / "info.yml"
    )

    if not info_file.exists():

        info = {
            "title": pretty_title,
            "description": ""
        }

        info_file.write_text(
            yaml.safe_dump(
                info,
                allow_unicode=True,
                sort_keys=False
            ),
            encoding="utf-8"
        )

    total = len(
        album["images"]
    )

    digits = max(
        2,
        len(str(total))
    )

    for index, image_url in enumerate(
        album["images"],
        start=1
    ):

        extension = Path(
            urlparse(
                image_url
            ).path
        ).suffix.lower()

        if extension not in IMAGE_EXTENSIONS:
            extension = ".jpg"

        filename = (
            f"{index:0{digits}d}"
            f"{extension}"
        )

        destination = (
            album_dir
            / filename
        )

        if destination.exists():

            print(
                f"  [YA EXISTE] {filename}"
            )

            continue

        print(
            f"  Descargando {filename}"
        )

        download_image(
            image_url,
            destination
        )


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    albums = extract_albums(
        soup
    )

    print()
    print(
        f"Álbumes detectados: "
        f"{len(albums)}"
    )

    for album in albums:

        print(
            f"  - {album['title']}"
            f" ({len(album['images'])} imágenes)"
        )

    for album in albums:

        create_album(
            album
        )


if __name__ == "__main__":
    main()