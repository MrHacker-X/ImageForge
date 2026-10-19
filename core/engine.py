#!/usr/bin/env python3
"""ImageForge core logic."""
from __future__ import annotations

from .config import load_tool_data


import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from PIL import Image, ImageOps

from .utils import (
    console,
    format_bytes,
    make_table,
    print_error,
    print_info,
    print_success,
    print_tool_header,
    print_warning,
    prompt_confirm,
    prompt_menu,
    prompt_text,
    safe_filename,
    unique_path,
)

def _load_tool_data(filename: str) -> dict:
    """Thin alias: load this tool's own config via core/config.py."""
    return load_tool_data(filename)

SUPPORTED_IMAGE_EXTENSIONS: Set[str] = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
}


@dataclass
class ImageOperationConfig:
    target_format: Optional[str] = None  # jpg | png | webp | bmp | tiff
    resize_width: Optional[int] = None
    resize_height: Optional[int] = None
    preserve_aspect: bool = True
    quality: Optional[int] = None  # 1..100 compression quality
    crop_box: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom)
    crop_aspect: Optional[Tuple[int, int]] = None  # e.g. (16, 9) or (1, 1)
    rotate_angle: Optional[float] = None  # degrees counter-clockwise or clockwise
    flip_horizontal: bool = False
    flip_vertical: bool = False
    rename_prefix: str = ""
    rename_suffix: str = ""
    rename_number_padding: Optional[int] = None  # e.g. 3 -> _001, _002
    rename_start_index: int = 1
    filter_formats: Optional[Set[str]] = None  # e.g. {"jpg", "png"}
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    output_dir: Optional[Path] = None
    overwrite_originals: bool = False


@dataclass
class ImageProcessItemResult:
    source_path: Path
    output_path: Optional[Path]
    status: str  # success | skipped | failed
    original_size: int = 0
    processed_size: int = 0
    original_dimensions: Tuple[int, int] = (0, 0)
    processed_dimensions: Tuple[int, int] = (0, 0)
    message: str = ""


@dataclass
class ImageProcessingSummary:
    results: List[ImageProcessItemResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.status == "success")

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.status == "skipped")

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.status == "failed")

    @property
    def total_original_bytes(self) -> int:
        return sum(r.original_size for r in self.results if r.status == "success")

    @property
    def total_processed_bytes(self) -> int:
        return sum(r.processed_size for r in self.results if r.status == "success")

    @property
    def bytes_delta(self) -> int:
        return self.total_processed_bytes - self.total_original_bytes


TOOL_DATA = _load_tool_data("format_capabilities.json")
FORMAT_MAP: Dict[str, Tuple[str, str]] = {
    _fmt_key: (_fmt_entry["pil_format"], _fmt_entry["extension"])
    for _fmt_key, _fmt_entry in TOOL_DATA.get("formats", {}).items()
    if isinstance(_fmt_entry, dict) and "pil_format" in _fmt_entry
}
DEFAULT_PROCESSED_DIR = TOOL_DATA.get("default_output_dir", "processed_images")


def collect_images(targets: Sequence[Path | str], recursive: bool = False) -> List[Path]:
    """Gather supported image files from file paths or directories."""
    files: List[Path] = []
    for item in targets:
        p = Path(item).expanduser().resolve()
        if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            files.append(p)
        elif p.is_dir():
            iterator = p.rglob("*") if recursive else p.iterdir()
            for child in sorted(iterator):
                if child.is_file() and child.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    files.append(child)
    return files


def _apply_center_aspect_crop(img: Image.Image, ratio_w: int, ratio_h: int) -> Image.Image:
    w, h = img.size
    target_ratio = float(ratio_w) / float(ratio_h)
    current_ratio = float(w) / float(h)
    if abs(current_ratio - target_ratio) < 1e-4:
        return img
    if current_ratio > target_ratio:
        new_w = int(round(h * target_ratio))
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(round(w / target_ratio))
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def _apply_resize(
    img: Image.Image,
    width: Optional[int],
    height: Optional[int],
    preserve_aspect: bool,
) -> Image.Image:
    orig_w, orig_h = img.size
    if width is None and height is None:
        return img

    if preserve_aspect:
        if width and height:
            scale = min(width / orig_w, height / orig_h)
            new_w = max(1, int(round(orig_w * scale)))
            new_h = max(1, int(round(orig_h * scale)))
        elif width:
            new_w = max(1, width)
            new_h = max(1, int(round(orig_h * (width / orig_w))))
        else:
            assert height is not None
            new_h = max(1, height)
            new_w = max(1, int(round(orig_w * (height / orig_h))))
    else:
        new_w = max(1, width if width else orig_w)
        new_h = max(1, height if height else orig_h)

    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def _passes_filters(
    path: Path,
    dimensions: Tuple[int, int],
    cfg: ImageOperationConfig,
) -> Tuple[bool, str]:
    ext_key = path.suffix.lower().lstrip(".")
    if ext_key == "jpeg":
        ext_key = "jpg"
    elif ext_key == "tif":
        ext_key = "tiff"

    if cfg.filter_formats:
        norm_filters = {
            ("jpg" if f.lower().lstrip(".") == "jpeg" else ("tiff" if f.lower().lstrip(".") == "tif" else f.lower().lstrip(".")))
            for f in cfg.filter_formats
        }
        if ext_key not in norm_filters:
            return (False, f"Format .{ext_key} excluded by format filter")

    w, h = dimensions
    if cfg.min_width and w < cfg.min_width:
        return (False, f"Width {w}px < min_width {cfg.min_width}px")
    if cfg.min_height and h < cfg.min_height:
        return (False, f"Height {h}px < min_height {cfg.min_height}px")
    if cfg.max_width and w > cfg.max_width:
        return (False, f"Width {w}px > max_width {cfg.max_width}px")
    if cfg.max_height and h > cfg.max_height:
        return (False, f"Height {h}px > max_height {cfg.max_height}px")

    return (True, "")


def _build_output_path(
    source: Path,
    sequence_index: int,
    cfg: ImageOperationConfig,
) -> Tuple[Path, str]:
    """Return (destination_path, pil_format_name)."""
    if cfg.target_format:
        fmt_key = cfg.target_format.lower().lstrip(".")
        if fmt_key not in FORMAT_MAP:
            raise ValueError(f"Unsupported target format: {cfg.target_format}")
        pil_format, out_ext = FORMAT_MAP[fmt_key]
    else:
        src_key = source.suffix.lower().lstrip(".")
        pil_format, out_ext = FORMAT_MAP.get(src_key, ("PNG", ".png"))

    stem = source.stem
    if cfg.rename_prefix or cfg.rename_suffix or cfg.rename_number_padding is not None:
        num_part = ""
        if cfg.rename_number_padding is not None and cfg.rename_number_padding > 0:
            num_part = f"_{sequence_index:0{cfg.rename_number_padding}d}"
        new_stem = f"{cfg.rename_prefix}{stem}{cfg.rename_suffix}{num_part}"
        new_stem = safe_filename(new_stem, default=stem)
    else:
        new_stem = stem

    if cfg.overwrite_originals and cfg.output_dir is None and out_ext == source.suffix.lower() and new_stem == stem:
        return (source, pil_format)

    out_dir = cfg.output_dir if cfg.output_dir is not None else (source.parent / DEFAULT_PROCESSED_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate = out_dir / f"{new_stem}{out_ext}"
    if candidate == source and not cfg.overwrite_originals:
        candidate = out_dir / f"{new_stem}_processed{out_ext}"
    if not cfg.overwrite_originals:
        candidate = unique_path(candidate)
    return (candidate, pil_format)


def process_images(
    targets: Sequence[Path | str],
    config: ImageOperationConfig,
    recursive: bool = False,
) -> ImageProcessingSummary:
    """Process one or more images or directories using the provided configuration."""
    files = collect_images(targets, recursive=recursive)
    summary = ImageProcessingSummary()
    seq_num = config.rename_start_index

    for fpath in files:
        try:
            orig_size = fpath.stat().st_size
            with Image.open(fpath) as img:
                orig_dims = img.size
                allowed, reason = _passes_filters(fpath, orig_dims, config)
                if not allowed:
                    summary.results.append(
                        ImageProcessItemResult(
                            source_path=fpath,
                            output_path=None,
                            status="skipped",
                            original_size=orig_size,
                            original_dimensions=orig_dims,
                            message=reason,
                        )
                    )
                    continue

                work_img = img.copy()

                # 1. Crop (explicit box or aspect ratio)
                if config.crop_box is not None:
                    l, t, r, b = config.crop_box
                    w, h = work_img.size
                    box = (
                        max(0, min(l, w - 1)),
                        max(0, min(t, h - 1)),
                        max(1, min(r, w)),
                        max(1, min(b, h)),
                    )
                    if box[2] > box[0] and box[3] > box[1]:
                        work_img = work_img.crop(box)
                elif config.crop_aspect is not None:
                    rw, rh = config.crop_aspect
                    work_img = _apply_center_aspect_crop(work_img, rw, rh)

                # 2. Resize
                if config.resize_width is not None or config.resize_height is not None:
                    work_img = _apply_resize(
                        work_img,
                        config.resize_width,
                        config.resize_height,
                        config.preserve_aspect,
                    )

                # 3. Rotate
                if config.rotate_angle is not None and config.rotate_angle != 0:
                    work_img = work_img.rotate(-float(config.rotate_angle), expand=True)

                # 4. Flip
                if config.flip_horizontal:
                    work_img = ImageOps.mirror(work_img)
                if config.flip_vertical:
                    work_img = ImageOps.flip(work_img)

                dest_path, pil_format = _build_output_path(fpath, seq_num, config)
                seq_num += 1

                # Convert RGBA/P to RGB for formats that don't support alpha (JPEG, BMP)
                if pil_format in ("JPEG", "BMP") and work_img.mode not in ("RGB", "L"):
                    if work_img.mode in ("RGBA", "LA") or (
                        work_img.mode == "P" and "transparency" in work_img.info
                    ):
                        rgba = work_img.convert("RGBA")
                        bg = Image.new("RGB", rgba.size, (255, 255, 255))
                        bg.paste(rgba, mask=rgba.split()[3])
                        work_img = bg
                    else:
                        work_img = work_img.convert("RGB")

                save_kwargs: Dict[str, Any] = {}
                if config.quality is not None:
                    q = max(1, min(100, int(config.quality)))
                    if pil_format in ("JPEG", "WEBP"):
                        save_kwargs["quality"] = q
                        save_kwargs["optimize"] = True
                    elif pil_format == "PNG":
                        save_kwargs["optimize"] = True
                        # Map quality 1..100 to compress_level 9..1
                        save_kwargs["compress_level"] = max(1, min(9, int(round((100 - q) / 11))))

                work_img.save(dest_path, format=pil_format, **save_kwargs)
                final_dims = work_img.size

            new_size = dest_path.stat().st_size
            summary.results.append(
                ImageProcessItemResult(
                    source_path=fpath,
                    output_path=dest_path,
                    status="success",
                    original_size=orig_size,
                    processed_size=new_size,
                    original_dimensions=orig_dims,
                    processed_dimensions=final_dims,
                    message=f"Saved as {pil_format}",
                )
            )
        except Exception as exc:
            summary.results.append(
                ImageProcessItemResult(
                    source_path=fpath,
                    output_path=None,
                    status="failed",
                    message=str(exc),
                )
            )

    return summary


def parse_crop_box(raw: str) -> Tuple[int, int, int, int]:
    """Parse 'left,top,right,bottom' or 'WxH+X+Y' into (left, top, right, bottom)."""
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 4:
        raise ValueError("Crop box must be 4 comma-separated integers: left,top,right,bottom")
    return (parts[0], parts[1], parts[2], parts[3])


def parse_aspect_ratio(raw: str) -> Tuple[int, int]:
    """Parse '16:9' or '1:1' into (w, h)."""
    sep = ":" if ":" in raw else "/"
    parts = [int(p.strip()) for p in raw.split(sep)]
    if len(parts) != 2 or parts[0] <= 0 or parts[1] <= 0:
        raise ValueError("Aspect ratio must be formatted as W:H (e.g. 16:9 or 1:1)")
    return (parts[0], parts[1])


def display_processing_summary(summary: ImageProcessingSummary) -> None:
    rows = []
    for r in summary.results:
        if r.status == "success":
            diff = r.processed_size - r.original_size
            diff_str = f"{'+' if diff > 0 else ''}{format_bytes(abs(diff))}"
            if diff < 0:
                diff_str = f"[green]-{format_bytes(abs(diff))}[/green]"
            elif diff > 0:
                diff_str = f"[yellow]+{format_bytes(diff)}[/yellow]"
            else:
                diff_str = "0 B"
            rows.append(
                (
                    r.source_path.name,
                    "[green]SUCCESS[/green]",
                    f"{r.original_dimensions[0]}x{r.original_dimensions[1]} -> {r.processed_dimensions[0]}x{r.processed_dimensions[1]}",
                    f"{format_bytes(r.original_size)} -> {format_bytes(r.processed_size)} ({diff_str})",
                    str(r.output_path),
                )
            )
        elif r.status == "skipped":
            rows.append(
                (
                    r.source_path.name,
                    "[yellow]SKIPPED[/yellow]",
                    f"{r.original_dimensions[0]}x{r.original_dimensions[1]}",
                    format_bytes(r.original_size),
                    r.message,
                )
            )
        else:
            rows.append(
                (
                    r.source_path.name,
                    "[bold red]FAILED[/bold red]",
                    "-",
                    "-",
                    r.message,
                )
            )

    console.print()
    if rows:
        console.print(
            make_table(
                title="ImageForge CLI - Operations Detail",
                columns=[
                    ("Source File", "bold cyan"),
                    ("Status", "white"),
                    ("Dimensions", "white"),
                    ("Size Change", "white"),
                    ("Output / Note", "dim white"),
                ],
                rows=rows,
            )
        )

    total_diff = summary.bytes_delta
    diff_label = (
        f"[green]-{format_bytes(abs(total_diff))} saved[/green]"
        if total_diff < 0
        else f"+{format_bytes(total_diff)}"
    )
    console.print(
        make_table(
            title="ImageForge Processing Summary",
            columns=[("Metric", "bold cyan"), ("Value", "white")],
            rows=[
                ("Successful Operations", f"[green]{summary.success_count}[/green]"),
                ("Skipped (Filtered)", f"[yellow]{summary.skipped_count}[/yellow]"),
                ("Failed Operations", f"[red]{summary.failed_count}[/red]"),
                ("Original Total Size", format_bytes(summary.total_original_bytes)),
                ("Processed Total Size", format_bytes(summary.total_processed_bytes)),
                ("Net Size Difference", diff_label),
            ],
        )
    )
