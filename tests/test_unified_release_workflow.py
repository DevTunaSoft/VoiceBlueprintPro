"""A desktop release must include Android APK and AAB from the same tag."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    data = yaml.safe_load((ROOT / ".github/workflows" / name).read_text())
    data["on"] = data.pop(True, data.get("on"))
    return data


def test_release_waits_for_android_at_the_same_tag():
    jobs = workflow("electron-release.yml")["jobs"]
    assert "mobile" in jobs["release"]["needs"]
    mobile = jobs["mobile"]
    assert mobile["uses"] == "./.github/workflows/mobile-release.yml"
    assert mobile["with"]["release_ref"] == "${{ inputs.release_tag || github.ref_name }}"

    called = workflow("mobile-release.yml")
    assert "workflow_call" in called["on"]
    assert "android" in called["jobs"]
    assert "ios" not in called["jobs"]
    job = called["jobs"]["android"]
    assert "inputs.release_ref" in job["steps"][0]["with"]["ref"]
    assert "inputs.release_ref" in job["if"]
    validation = next(s for s in job["steps"] if s.get("name") == "Validate release source")
    assert "refs/tags/${RELEASE_REF}^{commit}" in validation["run"]
    assert "package.json" in validation["run"]

    steps = jobs["release"]["steps"]
    collect = next(s["run"] for s in steps if s.get("name") == "Collect phone binaries")
    assert "VoiceBlueprintPro-android-release" in collect
    for extension in ("apk", "aab"):
        assert f"android.{extension}" in collect
    assert ".ipa" not in collect
    assert next(i for i, s in enumerate(steps) if s.get("name") == "Collect phone binaries") < next(
        i for i, s in enumerate(steps) if s.get("name") == "Validate all platforms before creating a release"
    )


def test_legacy_mobile_tags_only_package_android():
    called = workflow("mobile-release.yml")
    release = called["jobs"]["release"]
    assert release["needs"] == ["android"]
    script = next(s["run"] for s in release["steps"] if s.get("name") == "Draft prerelease")
    assert "VoiceBlueprintPro-${TAG}.apk" in script
    assert "VoiceBlueprintPro-${TAG}.aab" in script
    assert ".ipa" not in script
