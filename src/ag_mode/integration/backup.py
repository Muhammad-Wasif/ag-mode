"""Backup and Rollback system.

Ensures all configuration changes and workspace modifications are atomic,
tracked with SHA-256 checksums, and completely reversible.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from ag_mode.config import get_backups_dir
from ag_mode.diagnostics.logger import logger


def calculate_sha256(file_path: Path) -> str:
    """Compute sha256 checksum of a file."""
    if not file_path.exists() or not file_path.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class BackupManager:
    """Manages snapshots, manifests, and rollbacks."""

    def __init__(self, backups_dir: Optional[Path] = None):
        self.backups_dir = backups_dir or get_backups_dir()
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, paths: List[Path], reason: str = "Pre-activation snapshot") -> str:
        """Create a timestamped backup of the given paths."""
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S_%f")
        snapshot_dir = self.backups_dir / timestamp_str
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        manifest: Dict[str, Any] = {
            "id": timestamp_str,
            "created_at": now.isoformat(),
            "reason": reason,
            "files": [],
        }

        for path in paths:
            if not path.exists():
                manifest["files"].append({
                    "original_path": str(path.resolve()),
                    "existed": False,
                    "rel_backup_path": None,
                    "sha256": None,
                })
                continue

            if path.is_file():
                rel_name = path.name
                dest = snapshot_dir / rel_name
                # Avoid collision if multiple files have same name
                counter = 1
                while dest.exists():
                    dest = snapshot_dir / f"{counter}_{path.name}"
                    counter += 1

                shutil.copy2(path, dest)
                manifest["files"].append({
                    "original_path": str(path.resolve()),
                    "existed": True,
                    "is_dir": False,
                    "rel_backup_path": dest.name,
                    "sha256": calculate_sha256(dest),
                })
            elif path.is_dir():
                dest_dir = snapshot_dir / path.name
                shutil.copytree(path, dest_dir, dirs_exist_ok=True)
                manifest["files"].append({
                    "original_path": str(path.resolve()),
                    "existed": True,
                    "is_dir": True,
                    "rel_backup_path": dest_dir.name,
                    "sha256": None,
                })

        # Save manifest.json inside snapshot directory
        manifest_file = snapshot_dir / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info("integration", f"Created backup snapshot {timestamp_str}", {"reason": reason, "items": len(paths)})
        return timestamp_str

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available backup snapshots ordered by newest first."""
        snapshots = []
        for entry in sorted(self.backups_dir.iterdir(), reverse=True):
            if entry.is_dir():
                manifest_file = entry / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        snapshots.append(data)
                    except Exception:
                        pass
        return snapshots

    def rollback(self, snapshot_id: Optional[str] = None) -> bool:
        """Rollback to a specific snapshot or to the latest one."""
        snapshots = self.list_snapshots()
        if not snapshots:
            logger.warning("integration", "Rollback failed: No backup snapshots available.")
            return False

        target_manifest: Optional[Dict[str, Any]] = None
        if snapshot_id:
            for s in snapshots:
                if s["id"] == snapshot_id:
                    target_manifest = s
                    break
            if not target_manifest:
                logger.error("error", f"Rollback failed: Snapshot {snapshot_id} not found.")
                return False
        else:
            target_manifest = snapshots[0]

        target_dir = self.backups_dir / target_manifest["id"]
        logger.info("integration", f"Initiating rollback to snapshot {target_manifest['id']}")

        success = True
        for item in target_manifest.get("files", []):
            orig = Path(item["original_path"])
            existed = item.get("existed", False)
            rel_name = item.get("rel_backup_path")

            if not existed:
                # If file did not exist originally, remove it if it was created
                if orig.exists():
                    try:
                        if orig.is_dir():
                            shutil.rmtree(orig)
                        else:
                            orig.unlink()
                    except Exception as e:
                        logger.error("error", f"Rollback failed removing newly created file {orig}: {e}")
                        success = False
            else:
                # Restore original file
                if not rel_name:
                    continue
                backup_item = target_dir / rel_name
                if not backup_item.exists():
                    logger.error("error", f"Rollback missing backup file {backup_item}")
                    success = False
                    continue

                try:
                    orig.parent.mkdir(parents=True, exist_ok=True)
                    if item.get("is_dir"):
                        if orig.exists():
                            shutil.rmtree(orig)
                        shutil.copytree(backup_item, orig, dirs_exist_ok=True)
                    else:
                        shutil.copy2(backup_item, orig)
                except Exception as e:
                    logger.error("error", f"Rollback failed restoring {orig}: {e}")
                    success = False

        if success:
            logger.success("integration", f"Rollback to snapshot {target_manifest['id']} completed successfully.")
        return success


backup_manager = BackupManager()
