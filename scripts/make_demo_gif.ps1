param(
    [string]$FFmpeg = 'ffmpeg'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SourceVideo = Join-Path $RepoRoot 'assets/VID_20260912_235052.mp4'
$OutputGif = Join-Path $RepoRoot 'assets/demo-six-rounds-1.5x.gif'
$VideoFilter = '[0:v]setpts=(PTS-STARTPTS)/1.5,fps=10,scale=640:-2:flags=lanczos,hqdn3d=2:1:2:1,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle'

& $FFmpeg -hide_banner -loglevel error -y -ss 0.8 -t 33.7 -i $SourceVideo -filter_complex $VideoFilter -an -loop 0 $OutputGif
if ($LASTEXITCODE -ne 0) { throw "FFmpeg failed with exit code $LASTEXITCODE" }
Get-Item -LiteralPath $OutputGif
