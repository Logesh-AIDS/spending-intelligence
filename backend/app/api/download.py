"""
Secure APK download endpoint.
Serves the Android APK with proper security headers.
"""
import hashlib
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["Download"])

# APK stored in backend/static/ — path relative to this file
APK_DIR = Path(__file__).parent.parent / "static"
APK_FILENAME = "spendcontrol.apk"
APK_PATH = APK_DIR / APK_FILENAME


def get_apk_checksum() -> str:
    """Compute SHA-256 of the APK for integrity verification."""
    if not APK_PATH.exists():
        return ""
    sha256 = hashlib.sha256()
    with open(APK_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


@router.get("/download/android")
def download_android_apk():
    """
    Serve the Android APK securely.
    - Content-Disposition forces download (not open in browser)
    - X-Content-Type-Options prevents MIME sniffing
    - No authentication required — public download
    """
    if not APK_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="APK not available yet. Check back soon."
        )

    return FileResponse(
        path=str(APK_PATH),
        media_type="application/vnd.android.package-archive",
        filename=APK_FILENAME,
        headers={
            # Force download, never execute in browser
            "Content-Disposition": f'attachment; filename="{APK_FILENAME}"',
            # Prevent MIME sniffing attacks
            "X-Content-Type-Options": "nosniff",
            # File integrity — client can verify download wasn't tampered
            "X-APK-SHA256": get_apk_checksum(),
            # Cache for 1 hour — avoids repeated downloads of same file
            "Cache-Control": "public, max-age=3600",
        }
    )


@router.get("/download/android/info")
def get_apk_info():
    """
    Returns APK metadata without downloading.
    Frontend uses this to show version and verify file integrity.
    """
    if not APK_PATH.exists():
        return {
            "available": False,
            "message": "APK not yet available"
        }

    size_bytes = APK_PATH.stat().st_size
    size_mb = round(size_bytes / (1024 * 1024), 1)

    return {
        "available": True,
        "filename": APK_FILENAME,
        "size_mb": size_mb,
        "sha256": get_apk_checksum(),
        "version": "1.0.0",
        "min_android": "Android 8.0+",
        "download_url": "/download/android",
    }
