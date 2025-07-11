"""
track_70mm_gui_plotly.py
------------------------
Tk-GUI + OpenCV + Plotly tracker for the 70 mm tick mark.
"""

import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import csv, os, tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# ── CONSTANTS ────────────────────────────────────────────
SCALE_MM_PER_PX   = 0.04904       # 77 mm / 1570 px
TEMPLATE_HALF     = 12            # template half-width (px)
MATCH_METHOD      = cv2.TM_CCOEFF
SMOOTH_WIN        = 7             # smoothing window (frames)
FONT              = cv2.FONT_HERSHEY_SIMPLEX
CROP_X, CROP_Y, CROP_W, CROP_H = 400, 1, 75, 600   # ruler strip

# ── GUI PICKER ───────────────────────────────────────────
root = tk.Tk(); root.withdraw()

video_path = filedialog.askopenfilename(
    title="Select input video", filetypes=[("Video","*.mp4 *.mov *.avi")])
if not video_path: raise SystemExit("No video selected.")

base = simpledialog.askstring("Output",
        "Enter base output file name (no extension):")
if not base: raise SystemExit("No output name provided.")

out_dir      = os.path.dirname(video_path)
out_video    = os.path.join(out_dir, base + ".mp4")
csv_path     = os.path.join(out_dir, base + ".csv")
html_path    = os.path.join(out_dir, base + ".html")

# ── GRAB REFERENCE FRAME ─────────────────────────────────
cap = cv2.VideoCapture(video_path)
if not cap.isOpened(): raise IOError("Cannot open video.")
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_MSEC, 1000)          # 1 s mark
ok, frame = cap.read()
if not ok: raise RuntimeError("Cannot read frame @1 s")

roi      = frame[CROP_Y:CROP_Y+CROP_H, CROP_X:CROP_X+CROP_W]
ref_rot  = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)
rot_h, rot_w = ref_rot.shape[:2]

# ── USER CLICKS 70 mm TICK ───────────────────────────────
ref_x = None
def click(ev,x,y,flags,parm):
    global ref_x
    if ev == cv2.EVENT_LBUTTONDOWN:
        ref_x = x
        cv2.destroyAllWindows()

cv2.namedWindow("Click 70 mm tick")
cv2.setMouseCallback("Click 70 mm tick", click)
print("🖱️  Click the 70 mm tick mark …")
while ref_x is None:
    cv2.imshow("Click 70 mm tick", ref_rot)
    if cv2.waitKey(1) & 0xFF == 27: break
cv2.destroyAllWindows()
if ref_x is None: raise RuntimeError("Reference not set.")
print(f"Reference x = {ref_x}")

# ── TEMPLATE FOR MATCHING ────────────────────────────────
x1, x2 = max(0, ref_x-TEMPLATE_HALF), min(rot_w-1, ref_x+TEMPLATE_HALF)
template = cv2.cvtColor(ref_rot[:, x1:x2], cv2.COLOR_BGR2GRAY)

# ── TRACK THROUGH VIDEO ─────────────────────────────────
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(out_video, fourcc, fps, (rot_w, rot_h))

frames, raw_mm = [], []
idx = 0
while True:
    ok, frame = cap.read()
    if not ok: break
    idx += 1

    roi = frame[CROP_Y:CROP_Y+CROP_H, CROP_X:CROP_X+CROP_W]
    roi_rot = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)
    gray    = cv2.cvtColor(roi_rot, cv2.COLOR_BGR2GRAY)

    _,_,_,loc = cv2.minMaxLoc(cv2.matchTemplate(gray, template, MATCH_METHOD))
    best_x = loc[0] + TEMPLATE_HALF
    dev_mm = (best_x - ref_x) * SCALE_MM_PER_PX

    frames.append(idx)
    raw_mm.append(dev_mm)

    # draw (raw) overlay
    cv2.line(roi_rot,(ref_x,0),(ref_x,rot_h),(0,0,255),2)
    cv2.line(roi_rot,(best_x,0),(best_x,rot_h),(0,255,0),1)
    cv2.putText(roi_rot, f"{dev_mm:+.2f} mm", (10,30), FONT, 0.6,
                (255,255,255),2)
    writer.write(roi_rot)

cap.release(); writer.release()

# ── SMOOTH & SAVE CSV ───────────────────────────────────
smoothed = pd.Series(raw_mm).rolling(SMOOTH_WIN, center=True).mean()
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Frame","Dev_mm_raw","Dev_mm_smooth"])
    for fr, r, s in zip(frames, raw_mm, smoothed):
        w.writerow([fr, f"{r:.3f}", f"{s:.3f}" if not pd.isna(s) else ""])

# ── PLOT WITH PLOTLY ────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=frames, y=raw_mm, mode="lines", name="Raw",
    line=dict(color="rgba(0,100,255,.3)", dash="dot")))
fig.add_trace(go.Scatter(
    x=frames, y=smoothed, mode="lines+markers", name="Smoothed",
    line=dict(color="red")))
fig.update_layout(
    title="Deviation of 70 mm Tick (Raw vs. Smoothed)",
    xaxis_title="Frame",
    yaxis_title="Deviation (mm)",
    plot_bgcolor="rgb(245,245,245)",
    hovermode="x unified",
    height=500)
fig.write_html(html_path)

# ── DONE ────────────────────────────────────────────────
messagebox.showinfo(
    "Complete",
    f"Outputs saved in:\n\n• {out_video}\n• {csv_path}\n• {html_path}"
)
