# Demo media

- **demo-24s-61s-1.5x.gif:** source interval 00:24–01:01, played at 1.5× speed; 640×360, 10 fps, approximately 24.7 seconds, silent and looping.
- **VID_20260912_235052.mp4:** complete original recording, 1280×720, approximately 109.5 seconds, with original audio.
- **vision-thumb.png / simulation-thumb.png:** thumb-extension development snapshots.
- **vision-scissors.png / simulation-scissors.png:** scissors development snapshots.
- **workflow.svg:** portrait workflow diagram displayed directly in the README.
- **manifest.json:** file hashes, sizes, and GIF timing.

The video and four screenshots are the author's project recordings. The GIF keeps the full scene framing, with resizing, light denoising, and palette reduction for a smaller download. The source MP4 is unchanged.

## Rebuild the GIF

With FFmpeg installed, run from PowerShell:

```powershell
.\scripts\make_demo_gif.ps1
# If FFmpeg is not on PATH:
.\scripts\make_demo_gif.ps1 -FFmpeg 'C:\path\to\ffmpeg.exe'
```

The script replaces the derived GIF and leaves the original video untouched. Update `manifest.json` when replacing media. The current GIF was generated with FFmpeg 7.1.1.
