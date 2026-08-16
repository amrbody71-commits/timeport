# Timeport

Stand somewhere that no longer exists.

Three 360° panoramas you can look around from the inside, each generated from a
historically-researched prompt rather than a vibe.

| Era | Where you are standing |
|---|---|
| **Manchester, 1750** | Market Place, before the mills |
| **Times Square, 1910** | Broadway at Seventh Avenue |
| **Alexandria, 1970** | The Corniche |

```bash
python -m http.server 8000     # then open index.html
```

## The seam problem, and the fix

A 2:1 equirectangular image has to wrap: its left edge must continue seamlessly
into its right edge, or the viewer sees a vertical tear behind them. Diffusion
models do not know that, and there is no edge for an inpaint to grab at the
boundary of a frame.

`generate_pano.py` fixes it in three stages:

| Stage | What runs |
|---|---|
| **generate** | `fal-ai/flux-lora` with an equirectangular LoRA, at 2:1 |
| **deseam** | Roll the image 50%, inpaint the centre strip with the **same LoRA**, roll back |
| **upscale** | `fal-ai/topaz/upscale/image` |

Rolling puts the wrap seam in the middle of the frame, where an ordinary inpaint
can reach it. Because the repair runs with the 360 LoRA still loaded, the mended
strip keeps equirectangular geometry instead of quietly reverting to normal
perspective — which is what happens if you inpaint with the base model.

```bash
python generate_pano.py --era manchester
python generate_pano.py --era manchester --seed 12345
python generate_pano.py --era all --skip-upscale
python generate_pano.py --era manchester --dry-run   # print the prompt, spend nothing
```

Reads `FAL_KEY` from the environment or `~/.fal/credentials.json`. No key is
stored in this repository.

## Why the prompts look like that

`prompts.py` is the actual research. Every prompt opens with the LoRA's trigger
phrase and closes with a photographic-realism clause, and each era carries an
`exclude` list saying what must **not** appear and why it is period-wrong.

That list is a manual QA checklist rather than a model input, and deliberately
so: FLUX.1-dev is guidance-distilled, and `fal-ai/flux-lora` exposes no
`negative_prompt` field, so exclusions cannot be passed to the model at all.
They are handled the only two ways that work — by describing the period-correct
thing positively and precisely, because diffusion models follow assertion far
better than negation, and by curating candidates against the checklist by eye.

## Licence

MIT — see [LICENSE](LICENSE). The panoramas in `assets/` are generated images,
included so the viewer has something to show.
