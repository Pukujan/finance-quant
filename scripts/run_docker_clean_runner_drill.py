"""Build a Docker image, run finance-quant verification, report results, and clean up.

Usage:
    python scripts/run_docker_clean_runner_drill.py
    python scripts/run_docker_clean_runner_drill.py --keep
    python scripts/run_docker_clean_runner_drill.py --help

Requires Docker on the host. Gracefully skips if Docker is unavailable.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "Dockerfile.drill.template"

IMAGE_NAME = "finance-quant-drill"
CONTAINER_NAME = "fq-drill-runner"


def docker_available() -> bool:
    """Return True if `docker info` succeeds."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def generate_dockerfile(template: Path | None = None) -> str:
    """Return the Dockerfile content from the template or inline fallback."""
    source = template or TEMPLATE_PATH
    if source and source.exists():
        return source.read_text(encoding="utf-8")
    return (
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY requirements-dev.txt .\n"
        "RUN pip install --no-cache-dir -r requirements-dev.txt\n"
        "COPY pyproject.toml .\n"
        "COPY finance_quant/ ./finance_quant/\n"
        "COPY scripts/ ./scripts/\n"
        "COPY tests/ ./tests/\n"
        "RUN pip install --no-cache-dir -e \".[test]\"\n"
        'CMD ["python", "-m", "finance_quant", "verify", "--phase-b"]\n'
    )


def prepare_build_context(content: str, tmp_dir: Path) -> Path:
    """Write Dockerfile and copy needed sources into a temp build context."""
    dockerfile = tmp_dir / "Dockerfile.drill"
    dockerfile.write_text(content, encoding="utf-8")

    for name in ("requirements-dev.txt", "pyproject.toml"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, tmp_dir / name)

    for subdir in ("finance_quant", "scripts", "tests"):
        src = ROOT / subdir
        if src.exists():
            dst = tmp_dir / subdir
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    return dockerfile


def build_image(tmp_dir: Path, image_tag: str) -> subprocess.CompletedProcess:
    """Run `docker build` and return the CompletedProcess."""
    return subprocess.run(
        ["docker", "build", "-f", str(tmp_dir / "Dockerfile.drill"), "-t", image_tag, str(tmp_dir)],
        capture_output=True,
        text=True,
        timeout=600,
    )


def run_container(image_tag: str, container_name: str) -> subprocess.CompletedProcess:
    """Run the container with the default CMD and return the CompletedProcess."""
    return subprocess.run(
        [
            "docker", "run", "--rm",
            "--name", container_name,
            image_tag,
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )


def cleanup(image_tag: str, container_name: str) -> None:
    """Best-effort removal of container and image."""
    subprocess.run(
        ["docker", "rm", "-f", container_name],
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        ["docker", "rmi", "-f", image_tag],
        capture_output=True,
        timeout=30,
    )


def run_drill(keep: bool = False, template: Path | None = None) -> int:
    """Full build-run-report lifecycle. Returns 0 on success, non-zero on failure."""
    if not docker_available():
        print("SKIP: Docker is not available on this host.")
        return 0

    print(f"[drill] Building image '{IMAGE_NAME}' ...")

    with tempfile.TemporaryDirectory(prefix="fq-drill-") as tmp_str:
        tmp_dir = Path(tmp_str)
        dockerfile_content = generate_dockerfile(template)
        prepare_build_context(dockerfile_content, tmp_dir)

        build_result = build_image(tmp_dir, IMAGE_NAME)
        if build_result.returncode != 0:
            print(f"FAIL: Docker build failed (rc={build_result.returncode})")
            print(build_result.stderr[-1000:] if len(build_result.stderr) > 1000 else build_result.stderr)
            if keep:
                print(f"[drill] --keep set; image '{IMAGE_NAME}' may remain.")
            else:
                cleanup(IMAGE_NAME, CONTAINER_NAME)
            return 1

        print(f"[drill] Image built. Running container '{CONTAINER_NAME}' ...")

        run_result = run_container(IMAGE_NAME, CONTAINER_NAME)

        if run_result.returncode == 0:
            print("PASS: finance-quant verification succeeded in container.")
            if run_result.stdout:
                print(run_result.stdout[-2000:] if len(run_result.stdout) > 2000 else run_result.stdout)
            cleanup(IMAGE_NAME, CONTAINER_NAME)
            return 0
        else:
            print(f"FAIL: Container run failed (rc={run_result.returncode})")
            if run_result.stderr:
                print(run_result.stderr[-1000:] if len(run_result.stderr) > 1000 else run_result.stderr)
            if run_result.stdout:
                print(run_result.stdout[-1000:] if len(run_result.stdout) > 1000 else run_result.stdout)
            if keep:
                print(f"[drill] --keep set; container '{CONTAINER_NAME}' and image '{IMAGE_NAME}' retained.")
            else:
                cleanup(IMAGE_NAME, CONTAINER_NAME)
            return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Docker clean-runner drill for finance-quant")
    parser.add_argument("--keep", action="store_true", help="Retain container/image on failure for inspection")
    parser.add_argument("--template", type=Path, default=None, help="Path to Dockerfile.drill template")
    args = parser.parse_args(argv)
    return run_drill(keep=args.keep, template=args.template)


if __name__ == "__main__":
    raise SystemExit(main())
