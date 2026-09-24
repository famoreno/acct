# Propuestas de Trabajos de Fin de Grado

Este repositorio contiene el catálogo de propuestas de Trabajos de Fin de Grado y materiales educativos relacionados, organizado como un sitio web estático con MkDocs y el tema Material for MkDocs.

## Descripción

El proyecto incluye:

- Propuestas de TFG en el área de **Robótica Móvil**
- Propuestas de TFG en **Automatización Industrial**
- Propuestas de TFG en **Visión Artificial**
- Propuestas de TFG en el área de **Salud**
- Proyectos y propuestas anteriores
- Guías y material de apoyo para trabajar con TwinCAT 3 en contextos de automatización

## Estructura del repositorio

- `mkdocs.yml`: configuración principal de MkDocs y navegación del sitio.
- `main.py`: script de soporte asociado al proyecto.
- `README.md`: documentación general del repositorio.
- `docs/`: contenido de la documentación.
  - `index.md`: página de inicio del portal.
  - `contenidos/`: propuestas de TFG organizadas por área temática.
    - `robotica/`: propuestas de robótica móvil.
    - `automatizacion/`: propuestas de automatización industrial.
    - `vision/`: propuestas de visión artificial.
    - `salud/`: propuestas en el área de salud.
    - `antiguos/`: propuestas y proyectos anteriores.
  - `images/`: recursos gráficos e ilustraciones.
  - `javascripts/`: scripts personalizados para la web.
  - `stylesheets/`: estilos personalizados.
  - `overrides/`: personalización del tema Material.
  - `pdfs/`: documentos PDF generados o almacenados.
- `.github/`: configuración y automatizaciones del repositorio.
- `.gitignore`: reglas de exclusión de Git.

## Requisitos

Necesitarás Python 3 y las dependencias de MkDocs:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install mkdocs mkdocs-material mkdocs-macros-plugin
```

## Cómo visualizar la documentación localmente

1. Entra al directorio del proyecto.
2. Ejecuta el servidor de MkDocs:

   ```bash
   mkdocs serve
   ```

3. Abre en tu navegador:

   ```bash
   http://localhost:8000
   ```

## Cómo compilar el sitio

Para generar la versión estática del sitio:

   ```bash
   mkdocs build
   ```

El resultado se genera normalmente en la carpeta `site/`.

## Contribuciones

Las contribuciones son bienvenidas. Si quieres mejorar el contenido, corregir errores o añadir nuevos ejemplos, puedes abrir un *issue* o enviar un pull request.

---

© 2026 famoreno Propuestas de TFE.
