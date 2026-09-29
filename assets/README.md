# Demo media

## Files

| File | Description |
|---|---|
| [demo-six-rounds-1.5x.gif](demo-six-rounds-1.5x.gif) | Six consecutive visible rounds, 1.5× playback, 640×360, 10 fps, 22.5 s, silent, looping; approximately 7.6 MB |
| [VID_20260912_235052.mp4](VID_20260912_235052.mp4) | Complete, unmodified source recording, 1280×720, approximately 30 fps, 109.5 s, original audio; approximately 38.4 MB |
| [manifest.json](manifest.json) | SHA-256 hashes, exact file sizes, source interval, and output properties |

The original recording was supplied by the repository author. The MP4 copy was
verified against the supplied file by SHA-256; it was not recompressed, cropped,
muted, or shortened.

The GIF selects source time **00:00.8 through 00:34.5**, spanning six visible
interactions. The opening camera adjustment is omitted. Round boundaries were
identified by visually checking the robot/player actions; no synchronized game
log was supplied. The final visible interaction is followed by the return toward
the next round, with the next player's response excluded.

The GIF preserves the scene framing, scales to 640×360, uses light denoising and a
96-color palette, and discards audio. Playback timestamps are divided by 1.5;
10 fps GIF timing rounds the output to 22.5 seconds. It is a presentation excerpt,
not a timing benchmark. Consult the original MP4 for full-resolution motion and
audio.

## Regenerate

Install FFmpeg separately for media processing; it is not a Python runtime
dependency of the robot demo. The published GIF was generated with FFmpeg 7.1.1.
From PowerShell in the repository root:

```powershell
.\scripts\make_demo_gif.ps1
# Or pass the actual executable path:
.\scripts\make_demo_gif.ps1 -FFmpeg 'C:\path\to\ffmpeg.exe'
```

The script overwrites only the derived GIF. Different FFmpeg builds may produce
different output bytes; update the manifest after intentionally changing media.

To verify the original video:

```powershell
Get-FileHash .\assets\VID_20260912_235052.mp4 -Algorithm SHA256
```

Expected SHA-256:

```text
2b2fb6ad52920f29a8cc26b907a708a6432422f5f8bcc758e9a8d5619d1fba88
```
