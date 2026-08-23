import os
import shutil
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Detect Vercel or read-only environment
is_vercel = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

is_writable = False
if not is_vercel:
    try:
        test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, ".writable_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        is_writable = True
    except Exception:
        is_writable = False

if is_vercel or not is_writable:
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))

def get_upload_dir() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def save_resume_file(file_bytes: bytes, filename: str) -> str:
    target_dir = get_upload_dir()
    clean_filename = filename.replace(" ", "_")
    filepath = os.path.join(target_dir, clean_filename)

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    logger.info(f"Resume saved successfully to {filepath}")
    return clean_filename

def get_resume_path(filename: Optional[str] = None) -> Optional[str]:
    target_dir = get_upload_dir()

    if filename:
        path = os.path.join(target_dir, filename)
        if os.path.exists(path):
            return path

    # Check for default PDF in uploads directory
    if os.path.exists(target_dir):
        for file in os.listdir(target_dir):
            if file.endswith((".pdf", ".docx")) and not file.startswith("."):
                return os.path.join(target_dir, file)

    # Fallback check local uploads folder
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    if os.path.exists(local_dir):
        for file in os.listdir(local_dir):
            if file.endswith((".pdf", ".docx")) and not file.startswith("."):
                return os.path.join(local_dir, file)

    return None

def list_uploaded_resumes() -> List[Dict[str, Any]]:
    target_dir = get_upload_dir()
    resumes = []
    if os.path.exists(target_dir):
        for fname in os.listdir(target_dir):
            if fname.endswith((".pdf", ".docx")) and not fname.startswith("."):
                fpath = os.path.join(target_dir, fname)
                resumes.append({
                    "filename": fname,
                    "size_bytes": os.path.getsize(fpath),
                    "modified_time": os.path.getmtime(fpath)
                })
    return resumes

def remove_resume_file(filename: str) -> bool:
    target_dir = get_upload_dir()
    filepath = os.path.join(target_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
