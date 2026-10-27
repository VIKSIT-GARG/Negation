"""Exercise real video encode/decode when the optional video extra is installed."""
from pathlib import Path
import pytest
from negationscope.dataset import construct
from negationscope.io import read_jsonl
from negationscope.media import attach_media, extract_frames


def test_real_frame_extraction(tmp_path):
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")
    video = tmp_path / "fixture.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 5, (32, 32))
    assert writer.isOpened()
    for value in (0, 50, 100, 150, 200):
        writer.write(np.full((32, 32, 3), value, dtype=np.uint8))
    writer.release()
    seeds = read_jsonl(Path(__file__).resolve().parents[1] / "data/scene_seeds.jsonl")[:1]
    rows = construct(seeds)[:2]
    manifest = [{"sample_id": r["sample_id"], "media_path": str(video)} for r in rows]
    attached = attach_media(rows, manifest)
    extracted = extract_frames(attached, tmp_path / "frames", count=3)
    assert len(extracted) == 2
    assert [f["frame_index"] for f in extracted[0]["frames"]] == [0, 2, 4]
    assert [f["time_seconds"] for f in extracted[0]["frames"]] == [0., .4, .8]
    assert all(Path(f["path"]).is_file() for f in extracted[0]["frames"])
    video.write_bytes(b"changed")
    with pytest.raises(ValueError, match="media changed"):
        extract_frames(attached, tmp_path / "frames", count=3)
