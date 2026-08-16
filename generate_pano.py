#!/usr/bin/env python
"""Three-stage 360 panorama pipeline for timeport.

  generate   fal-ai/flux-lora + equirectangular LoRA at 2:1
  deseam     roll 50%, inpaint the centre strip with the SAME LoRA, roll back
  upscale    fal-ai/topaz/upscale/image

Rolling puts the wrap seam in the middle of the frame, where an ordinary inpaint can
reach it. Because the inpaint runs with the 360 LoRA loaded, the repaired strip keeps
equirectangular geometry instead of reverting to normal perspective.

Usage:
  python generate_pano.py --era manchester
  python generate_pano.py --era manchester --seed 12345
  python generate_pano.py --era all --skip-upscale
  python generate_pano.py --era manchester --dry-run     # print the prompt, spend nothing
"""
import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from prompts import ERAS, ORDER

QUEUE = "https://queue.fal.run"
LORA = ("https://huggingface.co/Akbartus/Flux360-LORA/resolve/main/"
        "equirectangular_flux_lora_v3_000003072.safetensors")
GEN_MODEL = "fal-ai/flux-lora"
INPAINT_MODEL = "fal-ai/flux-lora/inpainting"
UPSCALE_MODEL = "fal-ai/topaz/upscale/image"

WIDTH, HEIGHT = 1408, 704          # 2:1, the LoRA's documented working size
SEAM_BAND = 0.28                   # fraction of width repainted at the seam
FEATHER = 0.25                     # fraction of the band that ramps in/out

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
ASSETS = os.path.join(HERE, "assets")


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def get_key():
    key = os.environ.get("FAL_KEY")
    if key:
        return key.strip()
    path = os.path.join(os.path.expanduser("~"), ".fal", "credentials.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            key = json.load(f).get("fal_key")
        if key:
            return key.strip()
    die("no fal key (set FAL_KEY or ~/.fal/credentials.json)")


def req(url, key, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    r.add_header("Authorization", f"Key {key}")
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        die(f"HTTP {e.code} from {url}\n{e.read().decode(errors='replace')[:1500]}")
    except urllib.error.URLError as e:
        die(f"network error: {e.reason}")


def run(model, payload, key, label, timeout=600):
    """Submit to the queue, poll to completion, return the result payload."""
    print(f"  -> {label} ({model})", file=sys.stderr)
    sub = req(f"{QUEUE}/{model}", key, payload)
    status_url, response_url = sub.get("status_url"), sub.get("response_url")
    if not status_url:
        die(f"unexpected submit response: {json.dumps(sub)[:600]}")
    start, last = time.time(), None
    while True:
        st = req(status_url, key)
        state = st.get("status")
        if state != last:
            print(f"     {state}", file=sys.stderr)
            last = state
        if state == "COMPLETED":
            break
        if state in ("FAILED", "ERROR"):
            die(f"{label} failed: {json.dumps(st)[:600]}")
        if time.time() - start > timeout:
            die(f"{label} timed out after {timeout}s (request {sub.get('request_id')})")
        time.sleep(2)
    return req(response_url, key)


def first_url(result):
    def walk(o):
        if isinstance(o, dict):
            u = o.get("url")
            if isinstance(u, str) and u.startswith("http"):
                yield u
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    for u in walk(result):
        return u
    die(f"no image in result: {json.dumps(result)[:600]}")


def fetch(url):
    r = urllib.request.Request(url, headers={"User-Agent": "timeport/1.0"})
    with urllib.request.urlopen(r, timeout=300) as resp:
        return resp.read()


def data_uri(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


def build_mask(w, h):
    """Black everywhere, white vertical band at centre with feathered edges.

    White marks the region to repaint. The band never reaches the outer edges, so the
    wrap columns themselves are preserved and only the discontinuity is rebuilt.
    """
    from PIL import Image
    mask = Image.new("L", (w, h), 0)
    band = int(w * SEAM_BAND)
    x0 = (w - band) // 2
    ramp = max(1, int(band * FEATHER))
    px = mask.load()
    for x in range(band):
        gx = x0 + x
        if x < ramp:
            v = int(255 * x / ramp)
        elif x > band - ramp:
            v = int(255 * (band - x) / ramp)
        else:
            v = 255
        for y in range(h):
            px[gx, y] = v
    return mask


def stage_generate(era_id, era, key, seed):
    from PIL import Image
    payload = {
        "prompt": era["prompt"],
        "image_size": {"width": WIDTH, "height": HEIGHT},
        "loras": [{"path": LORA, "scale": 1.0}],
        "guidance_scale": 2.5,      # the LoRA's documented setting for realistic scenes
        "num_inference_steps": 28,
        "output_format": "png",
        "enable_safety_checker": False,
    }
    if seed is not None:
        payload["seed"] = seed
    result = run(GEN_MODEL, payload, key, "generate")
    img = Image.open(io.BytesIO(fetch(first_url(result)))).convert("RGB")
    out = os.path.join(WORK, f"{era_id}-1-raw.png")
    img.save(out)
    used = result.get("seed")
    print(f"     saved {out}  {img.width}x{img.height}  seed={used}", file=sys.stderr)
    return out, used


def stage_deseam(era_id, era, key, src, seed):
    from PIL import Image, ImageChops
    img = Image.open(src).convert("RGB")
    w, h = img.size
    half = w // 2

    rolled = ImageChops.offset(img, half, 0)
    mask = build_mask(w, h)
    rolled.save(os.path.join(WORK, f"{era_id}-2a-rolled.png"))
    mask.save(os.path.join(WORK, f"{era_id}-2b-mask.png"))

    payload = {
        "prompt": era["prompt"],
        "image_url": data_uri(rolled),
        "mask_url": data_uri(mask.convert("RGB")),
        "image_size": {"width": w, "height": h},
        "loras": [{"path": LORA, "scale": 1.0}],
        "guidance_scale": 2.5,
        "num_inference_steps": 28,
        "strength": 0.85,
        "output_format": "png",
        "enable_safety_checker": False,
    }
    if seed is not None:
        payload["seed"] = seed
    result = run(INPAINT_MODEL, payload, key, "seam repair")
    patched = Image.open(io.BytesIO(fetch(first_url(result)))).convert("RGB")
    if patched.size != (w, h):
        patched = patched.resize((w, h), Image.LANCZOS)

    fixed = ImageChops.offset(patched, -half, 0)   # roll back
    out = os.path.join(WORK, f"{era_id}-3-seamless.png")
    fixed.save(out)
    print(f"     saved {out}", file=sys.stderr)
    return out


def stage_upscale(era_id, era, key, src):
    from PIL import Image
    payload = {
        "image_url": data_uri(Image.open(src).convert("RGB")),
        "model": "Standard V2",
        "upscale_factor": 4,
        "output_format": "png",
    }
    result = run(UPSCALE_MODEL, payload, key, "upscale", timeout=900)
    big = Image.open(io.BytesIO(fetch(first_url(result)))).convert("RGB")
    out = os.path.join(ASSETS, era["asset"])
    big.save(out, quality=92, optimize=True)
    mb = os.path.getsize(out) / 1048576
    print(f"     saved {out}  {big.width}x{big.height}  {mb:.1f} MB", file=sys.stderr)
    if big.width != big.height * 2:
        print(f"     WARNING: not 2:1 ({big.width}x{big.height})", file=sys.stderr)
    return out


def process(era_id, key, args):
    era = ERAS[era_id]
    print(f"\n=== {era['name']} {era['year']} — {era['place']} ===", file=sys.stderr)
    if args.dry_run:
        print(era["prompt"])
        print("\nQA checklist — none of these may appear:")
        for x in era["exclude"]:
            print(f"  - {x}")
        return
    if args.from_file:
        # Resume from an already-seamless file: upscale and publish only. Lets a keeper
        # from an earlier run be finished without paying to generate it again.
        stage_upscale(era_id, era, key, args.from_file)
        return
    src, used = stage_generate(era_id, era, key, args.seed)
    if not args.skip_deseam:
        src = stage_deseam(era_id, era, key, src, used)
    if not args.skip_upscale:
        stage_upscale(era_id, era, key, src)
    else:
        from PIL import Image
        out = os.path.join(ASSETS, era["asset"])
        Image.open(src).convert("RGB").save(out, quality=92, optimize=True)
        print(f"     saved {out} (no upscale)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description="Generate timeport 360 panoramas")
    p.add_argument("--era", default="manchester",
                   help="era id, or 'all' (%s)" % ", ".join(ORDER))
    p.add_argument("--seed", type=int, help="reproducible generation")
    p.add_argument("--skip-deseam", action="store_true")
    p.add_argument("--skip-upscale", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print prompt + QA list only")
    p.add_argument("--from-file", help="skip generation; upscale this seamless file and publish")
    a = p.parse_args()

    ids = ORDER if a.era == "all" else [a.era]
    for i in ids:
        if i not in ERAS:
            die(f"unknown era '{i}' (have: {', '.join(ORDER)})")

    os.makedirs(WORK, exist_ok=True)
    os.makedirs(ASSETS, exist_ok=True)
    key = None if a.dry_run else get_key()
    for i in ids:
        process(i, key, a)


if __name__ == "__main__":
    main()
