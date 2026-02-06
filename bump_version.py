"""
Bump Version - Script para publicar nuevas versiones
=====================================================
Automatiza el proceso de:
  1. Actualizar la versión en updater.py
  2. Hacer commit de los cambios
  3. Crear un tag de git
  4. Hacer push (código + tag)

Uso:
  python bump_version.py 1.1.0
  python bump_version.py 1.2.0 --message "Mejoras en descarga"
"""

import re
import sys
import subprocess
import argparse


def get_current_version():
    """Lee la versión actual desde updater.py"""
    with open("updater.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'CURRENT_VERSION\s*=\s*"([^"]*)"', content)
    return match.group(1) if match else "0.0.0"


def set_version(new_version):
    """Actualiza la versión en updater.py"""
    with open("updater.py", "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r'CURRENT_VERSION\s*=\s*"[^"]*"',
        f'CURRENT_VERSION = "{new_version}"',
        content,
    )

    with open("updater.py", "w", encoding="utf-8") as f:
        f.write(content)


def run_git(*args):
    """Ejecuta un comando git y retorna el resultado"""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ❌ Error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Publicar una nueva versión")
    parser.add_argument("version", help="Nueva versión (ej: 1.1.0)")
    parser.add_argument(
        "--message", "-m",
        default=None,
        help="Mensaje del release (opcional)",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="No hacer push automáticamente",
    )
    args = parser.parse_args()

    new_version = args.version.lstrip("v")
    current_version = get_current_version()
    tag = f"v{new_version}"
    message = args.message or f"Release v{new_version}"

    print(f"\n{'=' * 50}")
    print(f"  Publicar nueva versión")
    print(f"{'=' * 50}")
    print(f"  Actual:  v{current_version}")
    print(f"  Nueva:   v{new_version}")
    print(f"  Tag:     {tag}")
    print(f"  Mensaje: {message}")
    print(f"{'=' * 50}\n")

    # Confirmar
    confirm = input("¿Continuar? (s/N): ").strip().lower()
    if confirm not in ("s", "si", "sí", "y", "yes"):
        print("Cancelado.")
        sys.exit(0)

    # 1. Actualizar versión
    print(f"\n1️⃣  Actualizando versión en updater.py...")
    set_version(new_version)
    print(f"   ✅ Versión actualizada a {new_version}")

    # 2. Commit
    print(f"\n2️⃣  Creando commit...")
    run_git("add", "updater.py")
    run_git("commit", "-m", f"bump: v{new_version} - {message}")
    print(f"   ✅ Commit creado")

    # 3. Tag
    print(f"\n3️⃣  Creando tag {tag}...")
    run_git("tag", "-a", tag, "-m", message)
    print(f"   ✅ Tag {tag} creado")

    # 4. Push
    if not args.no_push:
        print(f"\n4️⃣  Subiendo cambios a GitHub...")
        run_git("push")
        run_git("push", "origin", tag)
        print(f"   ✅ Código y tag subidos")
        print(f"\n🚀 GitHub Actions compilará el .exe y creará el Release automáticamente.")
        print(f"   Revisa: https://github.com/AdrianMP-02/DescargaMusica/actions")
    else:
        print(f"\n⚠️  No se hizo push. Ejecuta manualmente:")
        print(f"   git push && git push origin {tag}")

    print(f"\n✅ ¡Listo! Versión v{new_version} preparada.\n")


if __name__ == "__main__":
    main()
