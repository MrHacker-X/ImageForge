#!/usr/bin/env python3
"""ImageForge CLI configuration constants (built-in, self-contained)."""
from __future__ import annotations

_CONFIGS: dict = {
    "defaults.json": {
        "tool": "imageforge",
        "name": "ImageForge CLI",
        "subtitle": "Bulk Image Processor",
        "version": "1.0.0",
        "description": "Image file(s) or directory path(s) to process",
        "homepage": "https://github.com/MrHacker-X/imageforge",
        "author": "MrHacker-X",
        "email": "contact@vritrasec.com",
        "website": "https://vritrasec.com",
        "network": "https://link.vritrasec.com",
        "about_overview": (
            "ImageForge is a bulk image processor built on Pillow: convert formats, resize with aspect preservation, center-crop to a ratio, rotate, flip and batch-rename whole folders in a single pass - every operation happens locally, with a summary of bytes saved."
        ),
        "about_features": [
            "Format conversion: JPG, PNG, WebP, BMP, TIFF",
            "Resize with (or without) aspect-ratio preservation",
            "Box crop, center-crop to aspect ratio, rotate, flip",
            "Quality-tuned compression for lossy formats",
            "Batch rename with prefix, suffix and numbering",
            "Dual interface: interactive menu or direct CLI flags",
        ]
    },
    "format_capabilities.json": {
        "formats": {
            "jpg": {
                "pil_format": "JPEG",
                "extension": ".jpg",
                "alpha_support": False
            },
            "jpeg": {
                "pil_format": "JPEG",
                "extension": ".jpg",
                "alpha_support": False
            },
            "png": {
                "pil_format": "PNG",
                "extension": ".png",
                "alpha_support": True
            },
            "webp": {
                "pil_format": "WEBP",
                "extension": ".webp",
                "alpha_support": True
            },
            "bmp": {
                "pil_format": "BMP",
                "extension": ".bmp",
                "alpha_support": False
            },
            "tiff": {
                "pil_format": "TIFF",
                "extension": ".tiff",
                "alpha_support": True
            },
            "tif": {
                "pil_format": "TIFF",
                "extension": ".tiff",
                "alpha_support": True
            }
        },
        "default_output_dir": "processed_images"
    }
}


def load_tool_data(filename: str) -> dict:
    """Return the built-in configuration table stored under `filename`."""
    return dict(_CONFIGS.get(filename, {}))


def load_defaults() -> dict:
    """Return the tool identity / defaults configuration."""
    return dict(_CONFIGS.get("defaults.json", {}))
