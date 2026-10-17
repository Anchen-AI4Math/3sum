"""Offline byte-integrity checks. Does not rebuild Lean or refresh remote state."""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import sys
import zipfile


ROOT = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def relative_name(name):
    path = PurePosixPath(name.replace("\\", "/"))
    check(not path.is_absolute() and ".." not in path.parts, f"Unsafe path: {name}")
    return path.as_posix()


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def main():
    listed = set()
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        name = relative_name(name)
        check(name not in listed, f"Duplicate manifest entry: {name}")
        check(digest((ROOT / name).read_bytes()) == expected, f"Archive hash mismatch: {name}")
        listed.add(name)
    actual = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS.txt"
        and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    # Only the top-level hash manifest is self-excluded.
    actual.update(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("SHA256SUMS.txt") if p.parent != ROOT)
    check(listed == actual, f"Manifest coverage mismatch: {sorted(listed ^ actual)}")

    native_hashes = read_json("evidence/bigospeedrun-official-final/source-sha256.json")
    for name, expected in native_hashes.items():
        check(digest((ROOT / "proof-source" / relative_name(name)).read_bytes()) == expected,
              f"Official source mismatch: {name}")
    check(len(native_hashes) == 689, "Unexpected official Lean source count")
    check(len(list((ROOT / "proof-source").rglob("*.lean"))) == 689, "Unexpected exported Lean source count")

    completion = read_json("evidence/mission-completion.json")
    for name, record in completion["evidence"].items():
        check(digest((ROOT / "evidence" / relative_name(name)).read_bytes()) == record["sha256"],
              f"Completion evidence mismatch: {name}")
    manifest_path = ROOT / "evidence/machine-platform-manifest.json"
    check(digest(manifest_path.read_bytes()) == completion["manifest_sha256"], "Platform manifest mismatch")
    manifest = read_json("evidence/machine-platform-manifest.json")
    platform_files = {entry["path"]: entry["sha256"] for entry in manifest["definitions"]}
    for entry in manifest["theorems"]:
        for prefix in ("theorem", "solution"):
            platform_files[entry[prefix + "_path"]] = entry[prefix + "_sha256"]
    check(len(platform_files) == 1003, "Unexpected platform source count")
    with zipfile.ZipFile(ROOT / "evidence/prove2me-source-export.zip") as archive:
        check(set(archive.namelist()) == set(platform_files), "Platform source membership mismatch")
        for name, expected in platform_files.items():
            check(digest(archive.read(name)) == expected, f"Platform source mismatch: {name}")

    catalogue = read_json("evidence/graph-snapshot-catalog.json")
    selected = [r for r in catalogue["records"] if r["included_in_key_responses_zip"]]
    with zipfile.ZipFile(ROOT / "evidence/prove2me-key-graph-responses.zip") as archive:
        check(set(archive.namelist()) == {relative_name(r["file"]) for r in selected},
              "Key graph response membership mismatch")
        for record in selected:
            check(digest(archive.read(relative_name(record["file"]))) == record["sha256"],
                  f"Graph response mismatch: {record['file']}")

    audit = read_json("evidence/bigospeedrun-official-audit.json")
    official = ROOT / "evidence/bigospeedrun-official-final"
    check(digest((official / "receipt.json").read_bytes()) == audit["receipt_sha256"], "Official receipt mismatch")
    check(digest((official / "artifact.zip").read_bytes()) == audit["artifact_archive_sha256"], "Official artifact mismatch")
    receipt = read_json("evidence/bigospeedrun-official-final/receipt.json")
    with zipfile.ZipFile(official / "artifact.zip") as archive:
        check(archive.testzip() is None, "Official ZIP CRC failure")
        check(archive.read("receipt.json") == (official / "receipt.json").read_bytes(), "Embedded receipt mismatch")
        for name, expected in receipt["artifact_sha256"].items():
            check(digest(archive.read(name)) == expected, f"Official artifact member mismatch: {name}")
    check(receipt["status"] == "passed", "Official receipt does not report passed")
    check(receipt["request"]["commit"] == completion["source_commit"], "Source commit mismatch")

    certificate_count = 0
    for line in (ROOT / "analytic-certificate/SHA256SUMS.txt").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        check(digest((ROOT / "analytic-certificate" / relative_name(name)).read_bytes()) == expected,
              f"Original analytic certificate mismatch: {name}")
        certificate_count += 1

    print(json.dumps({
        "archive_integrity": "passed",
        "archived_files_checked": len(listed),
        "official_lean_source_files_checked": len(native_hashes),
        "platform_source_files_checked": len(platform_files),
        "key_graph_response_files_checked": catalogue["archived_distinct_files"],
        "all_graph_snapshot_records_catalogued": len(catalogue["records"]),
        "official_artifact_files_checked": len(receipt["artifact_sha256"]),
        "original_certificate_checksums_checked": certificate_count,
        "source_commit": completion["source_commit"],
        "lean_build_rerun": False,
        "remote_status_refreshed": False
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print(f"ARCHIVE CHECK FAILED: {error}", file=sys.stderr)
        sys.exit(1)
