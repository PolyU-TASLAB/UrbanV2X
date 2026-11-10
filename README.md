Website for the UrbanV2X datasets.

Webpage: https://polyu-taslab.github.io/UrbanV2X/

If you have any suggestions or questions, do not hesitate to propose an issue.

If you find this repositorie is helpful in your research, a simple star or citation of our works should be the best affirmation for us. :blush: 

## Acknowledgement
The template from [ECMD](https://arclab-hku.github.io/ecmd/) dataset.

## Local preview

Run `python3 -m http.server 8080` in this directory and open `http://localhost:8080/`.
The 3D observation explorer loads local JSON over HTTP; opening `index.html` via
`file://` will not load those observations in most browsers.

## Experimental media

The overview order is: automatic cover reel, full presentation, dataset cards, collection sites,
three preview groups (surround sensing / reconstruction / combined positioning),
footer. Previews play automatically while visible, without opening individual
players. Only the full presentation exposes normal video controls.

`assets/previews/sources.json` records media provenance. The five cover loops total
about 2.1 MiB. Silent H.264 clips are used instead of larger GIFs, with lazy loading,
full-aspect presentation, 0.8 s loop crossfades and 0.8 s transitions between slides.
Reduced-motion preferences disable automatic playback. The full 41.9 s film is
a complete 720p web encode of the supplied `飞书20261110-151649.mp4`,
retaining every frame, and loads when viewed. The source remains unchanged locally.

The user-selected large-point LiDAR-camera experiment is used in the cover and
cards. Its embedded camera labels and footer are removed from the preview; labels
remain HTML. The front cameras are **cam1 and cam2**. The sensing preview uses seven
original JPEG streams without point overlays; extraction is recorded in
`assets/previews/surround-source.json`.

The positioning preview combines GT motion, satellite reception and UWB into one
scene, using the same 2026-08-13 recording. Positions come from RTK/INS GT. Red
satellites satisfy NAV-SAT ephAvail=1, elevation>=10 degrees, C/N0=0 and qualityInd<=1:
these are NLOS candidates, not verified building blockage. Azimuth/elevation come
from receiver observations; satellite radius and receiver height are for display.
UWB nodes 1, 3 and 4 use the roundabout, west and east-near-roundabout
positions in `all_lampposts_latlon(1).xlsx`. The ID associations are inferred by
matching recorded ranges during vehicle motion against the tabulated WGS84
positions, without fitting coordinates or changing raw measurements. Node 18
remains unmapped. `scripts/resolve_uwb_anchors.py` records candidate comparisons
in `assets/data/uwb-anchor-mapping.json`; spreadsheet heights are not assumed
to be antenna heights. Lines appear only at epochs with a recorded range. Missing
readings remain gaps. OSM attribution is displayed in HTML; height assumptions are retained in the cached map metadata.
The homepage positioning block is a lightweight interactive demo, not a separate
dataset product. It loads its scene data near the viewport, autoplays the moving
segment (timeline indices 225–299), and keeps playing during mouse/touch rotation.
It supports pause, seeking, zoom and a viewpoint reset. GT positions are linearly
interpolated for display; satellite/range observations stay at their recorded epochs.
Loop transitions crossfade over 0.8 seconds without resetting the viewing angle.
Reduced-motion preferences disable autoplay. The optional `positioning/` page uses
the same viewer. Detailed legends, technical notes and the separate UWB chart are
not shown in the demo UI. The dataset card describes raw GNSS/UWB measurements,
with a static OSM scene of the GT trajectory, UWB connection and satellite rays.
`capture_positioning_card.py` renders epoch 281, which has an actual measurement
to a mapped UWB anchor, without embedding any text in the image.

The collection-site section uses the two complete Figure 8 panels from the paper,
showing routes and roadside locations at HKSTP and East Kowloon. This is the
user-requested exception to using original experiment media: the route figures
retain their original annotations and are encoded as WebP without cropping.

The Sensors page follows the sensor platform section and specification table in
`paper/main.tex`, including CAN measurements and C-V2X communication. The rig-side
overview covers cameras, LiDAR/radar, IMU/CAN, GNSS/UWB, ground truth and C-V2X.
Sky-pointing imagery and GPAL-Ares-R7861 radar are identified as original-release
equipment, using the original downloads and `paper/legacy/main.tex`. Its two
specification tables have only Sensor and Specifications & output columns.
The page opens with the vehicle photograph from `assets/img/calibration.png`,
using responsive, uncropped WebP derivatives and a link to the original PNG,
followed immediately by the system architecture, the onboard sensor rig and the
onboard/roadside specification tables. `prepare_sensor_figures.py` copies
the two user-supplied JPEGs (`20261110-223054.jpg` and `20261110-223919.jpg`)
byte-for-byte. The architecture introduction also covers synchronization; there
is no separate synchronization section. The two images total approximately 650 KiB.

Scripts in `scripts/` read source datasets and write website assets only. Raw
source bags are never changed. Dependencies: FFmpeg, NumPy, OpenCV, rosbags;
Playwright is used to capture the data-driven 3D canvas for compressed previews.
Reference boxes remain original draft annotations, not independently verified GT.

## Calibration downloads and navigation

The Calibration page opens with the sensor-frame figure, coordinate-frame explanations
and transform equation, followed by parameter downloads. The Frame / Sensor / Topic
table is omitted; its accompanying text is retained. File conventions are also in
the downloadable README. `scripts/prepare_calibration_downloads.py`
copies the supplied 7 intrinsic and 38 extrinsic YAMLs byte-for-byte into
`assets/calibration/`, and generates grouped ZIPs, a format guide and SHA-256
checksums. It also copies all 24 roadside parameter/documentation files and the
lamppost coordinate workbook without modification. The complete ZIP contains
70 source files (45 onboard YAMLs, 24 roadside files, one XLSX), plus format
documentation and checksums, and is about 73 KiB. The eight roadside poses map
sensor frames to separate HKSTP/East Kowloon public ENU origins using `T_Rj`;
quaternions are `[w, x, y, z]`. The spreadsheet positions are lamppost positions,
not replacements for the supplied sensor extrinsics.
The source package is `august_2026_reviewed_candidate` and retains
`calibration_accepted: false`; no parameter values or acceptance fields are edited.
The `Camera-IMU` directory maps IMU to camera, and the original `ap128p` file
identifier is retained for AT128P. Structural rotation and inverse checks validate
file handling, not calibration accuracy. These parameter files are committed with the website and served through GitHub Pages.

Download opens at the Hugging Face dataset homepage and documents the verified
`hkstp_s_01` / `hkstp_l_01` directory layout (checked through the public HF API).
It retains original Small/Large Loop filenames, sizes, roadside coordinates, GNSS
RINEX links, the Large Loop Baidu mirror, and the ROS/TUM schema. Legacy GNSS
copy-paste descriptions were corrected. The original sequence GIFs are encoded
as lazy-loaded, muted 14-second MP4 loops (about 0.4 MiB each) with crossfaded
seams. Statistics and generic product presentation sections remain omitted.

All six pages use `assets/css/navigation.css` and the shared menu handler in
`assets/js/site.js`. Run `python scripts/sync_navigation.py` after changing the
common header to keep labels, links and active-page states consistent.

## Publishing and loading budget

GitHub Pages publishes the root of `main`. Push website updates to `Qijun`, then
merge into `main`. Check the Pages build and the deployed commit after merging.

Publish assets used by the current pages; retain unused renders and intermediate
media locally. Keep short previews below 1.2 MiB and the complete film below
10 MiB. The current film is about 8.1 MiB, versus 43.5 MiB for the source.
All videos use `preload="none"`; clips play when visible, and posters for content
below the fold load near the viewport. The interactive positioning JSON is also
deferred until its section approaches the viewport.

The vehicle photo uses 640/1280/1760-pixel WebP alternatives (65/227/384 KiB),
with the 4.5 MiB original available on click. DM Sans and Manrope Latin variable
fonts are served locally as WOFF2 with `font-display: swap`; licenses are in
`assets/fonts/`. Page rendering has no Google Fonts dependency.

Run `python scripts/check_site.py --tracked` before publishing. The Website checks
workflow checks linked files, image/video size budgets, deferred video loading,
JavaScript syntax and calibration checksums on `Qijun` and `main`. Regenerate the
web photo and film using `scripts/optimize_site_media.py --film-source <original>`.
