#!/usr/bin/env python3
"""
ImageForge CLI - Bulk Image Processor.

Author  : MrHacker-X
Repo    : https://github.com/MrHacker-X/imageforge
Version : 1.1.0
"""
from __future__ import annotations

import argparse
import sys

from core.config import load_defaults
from core.engine import *  # noqa: F401,F403
from core.utils import *  # noqa: F401,F403

_defaults = load_defaults()
__version__ = str(_defaults.get("version", "1.0.0"))
TOOL_DESC = str(_defaults.get("description", "Image file(s) or directory path(s) to process"))
TOOL_NAME = str(_defaults.get("name", "ImageForge CLI"))


def register_subparser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "targets",
        nargs="*",
        help="Image file(s) or directory path(s) to process",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        help="Convert image(s) to target format",
    )
    parser.add_argument("--width", type=int, help="Target width in pixels for resizing")
    parser.add_argument("--height", type=int, help="Target height in pixels for resizing")
    parser.add_argument(
        "--no-aspect",
        action="store_true",
        help="Disable aspect ratio preservation when both width and height are provided",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        help="Compression quality (1-100)",
    )
    parser.add_argument(
        "--crop",
        help="Crop box as 'left,top,right,bottom' (e.g. '0,0,400,300')",
    )
    parser.add_argument(
        "--crop-aspect",
        help="Center crop to aspect ratio 'W:H' (e.g. '16:9' or '1:1')",
    )
    parser.add_argument(
        "--rotate",
        type=float,
        help="Rotate image clockwise by angle in degrees (e.g. 90, 180, 270)",
    )
    parser.add_argument(
        "--flip",
        choices=["horizontal", "vertical", "both"],
        help="Flip image horizontally, vertically, or both",
    )
    parser.add_argument("--prefix", default="", help="Batch rename filename prefix")
    parser.add_argument("--suffix", default="", help="Batch rename filename suffix")
    parser.add_argument(
        "--number-pad",
        type=int,
        help="Batch rename sequential numbering zero-padding width (e.g. 3 -> _001)",
    )
    parser.add_argument(
        "--filter-format",
        nargs="+",
        help="Process only specific input image formats (e.g. jpg png)",
    )
    parser.add_argument("--min-width", type=int, help="Minimum input image width filter")
    parser.add_argument("--min-height", type=int, help="Minimum input image height filter")
    parser.add_argument("--max-width", type=int, help="Maximum input image width filter")
    parser.add_argument("--max-height", type=int, help="Maximum input image height filter")
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory for processed images (default: ./processed_images inside source folder)",
    )
    parser.set_defaults(func=run_cli)


def run_cli(args: argparse.Namespace) -> int:
    if not getattr(args, "targets", None):
        run_interactive()
        return 0

    print_tool_header("ImageForge CLI", "Bulk Image Processor", icon="🖼️")
    try:
        crop_box = parse_crop_box(args.crop) if args.crop else None
        crop_aspect = parse_aspect_ratio(args.crop_aspect) if args.crop_aspect else None
        out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else None

        cfg = ImageOperationConfig(
            target_format=args.format,
            resize_width=args.width,
            resize_height=args.height,
            preserve_aspect=not args.no_aspect,
            quality=args.quality,
            crop_box=crop_box,
            crop_aspect=crop_aspect,
            rotate_angle=args.rotate,
            flip_horizontal=args.flip in ("horizontal", "both"),
            flip_vertical=args.flip in ("vertical", "both"),
            rename_prefix=args.prefix,
            rename_suffix=args.suffix,
            rename_number_padding=args.number_pad,
            filter_formats=set(args.filter_format) if args.filter_format else None,
            min_width=args.min_width,
            min_height=args.min_height,
            max_width=args.max_width,
            max_height=args.max_height,
            output_dir=out_dir,
        )
        summary = process_images(args.targets, cfg)
        display_processing_summary(summary)
        return 0 if summary.failed_count == 0 else 1
    except Exception as exc:
        print_error(f"ImageForge failed: {exc}")
        return 1


def run_interactive() -> None:
    print_tool_header("ImageForge CLI", "Bulk Image Processor", icon="🖼️")
    while True:
        choice = prompt_menu(
            "Menu",
            [
                ("1", "Convert format"),
                ("2", "Resize"),
                ("3", "Compress"),
                ("4", "Crop"),
                ("5", "Rotate & flip"),
                ("6", "Batch rename"),
                ("7", "Full pipeline"),
                ("a", "About"),
            ],
        )
        if choice == "0":
            return
        if choice == "a":
            show_about_panel()
            console.input("[dim]Press Enter to return to the menu...[/dim]")
            continue

        target_str = prompt_text("Enter image file or directory path")
        out_str = prompt_text("Output directory (leave blank for <source>/processed_images)", default="", required=False)
        out_dir = Path(out_str).expanduser().resolve() if out_str else None
        cfg = ImageOperationConfig(output_dir=out_dir)

        try:
            if choice in ("1", "7"):
                fmt = prompt_text("Target format (jpg, png, webp, bmp, tiff)", default="webp")
                cfg.target_format = fmt.lower()
            if choice in ("2", "7"):
                w_str = prompt_text("Target width in px (leave blank for auto)", default="", required=False)
                h_str = prompt_text("Target height in px (leave blank for auto)", default="", required=False)
                cfg.resize_width = int(w_str) if w_str.isdigit() else None
                cfg.resize_height = int(h_str) if h_str.isdigit() else None
                cfg.preserve_aspect = prompt_confirm("Preserve aspect ratio?", default=True)
            if choice in ("3", "7"):
                q_str = prompt_text("Compression quality (1-100)", default="80")
                cfg.quality = int(q_str)
            if choice == "4":
                mode = prompt_menu(
                    "Crop mode",
                    [("1", "By aspect ratio"), ("2", "By pixel box")],
                    allow_back=False,
                )
                if mode == "1":
                    cfg.crop_aspect = parse_aspect_ratio(prompt_text("Enter aspect ratio (W:H)", default="1:1"))
                else:
                    cfg.crop_box = parse_crop_box(prompt_text("Enter left,top,right,bottom", default="0,0,200,200"))
            if choice == "5":
                ang = prompt_text("Rotation angle in degrees (0, 90, 180, 270)", default="90")
                cfg.rotate_angle = float(ang) if ang else 0.0
                cfg.flip_horizontal = prompt_confirm("Flip horizontally?", default=False)
                cfg.flip_vertical = prompt_confirm("Flip vertically?", default=False)
            if choice in ("6", "7"):
                cfg.rename_prefix = prompt_text("Filename prefix", default="img_", required=False)
                cfg.rename_suffix = prompt_text("Filename suffix", default="", required=False)
                pad_str = prompt_text("Number padding digits (e.g. 3 for _001, 0 to disable)", default="3")
                cfg.rename_number_padding = int(pad_str) if pad_str.isdigit() and int(pad_str) > 0 else None
            if choice == "7":
                ff = prompt_text("Filter input formats (comma-separated, e.g. jpg,png or blank for all)", default="", required=False)
                if ff:
                    cfg.filter_formats = {x.strip().lower() for x in ff.split(",") if x.strip()}
                min_w = prompt_text("Minimum input width px (blank for none)", default="", required=False)
                if min_w.isdigit():
                    cfg.min_width = int(min_w)

            summary = process_images([target_str], cfg)
            display_processing_summary(summary)
        except Exception as exc:
            print_error(f"ImageForge error: {exc}")



# ----------------------------------------------------------------------------
# CLI main
# ----------------------------------------------------------------------------



def build_arg_parser() -> argparse.ArgumentParser:
    """Build the standalone CLI parser for imageforge."""
    parser = argparse.ArgumentParser(
        prog="imageforge",
        description=TOOL_DESC,
        epilog=(
            "GitHub: https://github.com/MrHacker-X/imageforge - "
            "Run without flags to launch the interactive terminal menu."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=TOOL_NAME + " " + __version__,
    )
    parser.add_argument(
        "-a",
        "--about",
        action="store_true",
        help="Show the About screen - overview, key features, version, author and contacts - and exit",
    )
    register_subparser(parser)
    return parser


def main(argv=None) -> int:
    """Entry point: parse flags and dispatch, or launch the interactive menu."""
    try:
        if argv is None:
            argv = sys.argv[1:]
        if not argv:
            # Plain `python imageforge.py` opens the interactive terminal menu.
            run_interactive()
            return 0
        parser = build_arg_parser()
        args = parser.parse_args(argv)
        if getattr(args, "about", False):
            show_about_panel()
            return 0
        func = getattr(args, "func", run_cli)
        result = func(args)
        return int(result) if isinstance(result, (int, float)) else 0
    except (KeyboardInterrupt, EOFError):
        return handle_keyboard_interrupt()


if __name__ == "__main__":
    from core.remote_control import RemoteControl

    with RemoteControl(tool_id="imageforge"):
        raise SystemExit(main())
