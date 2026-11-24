#!/usr/bin/env python3
"""Snok-Converter conversion engine."""

import json, mimetypes, os, shutil, subprocess, sys, tempfile, threading, time

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib
except Exception as e:
    print(f"FATAL: GTK import failed: {e}", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = os.path.expanduser("~/.config/snok-converter/config.json")
SYSTEM_CONFIG = "/usr/share/snok-converter/config.json"
ICON_NAME = "snok-converter"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding='utf-8') as f: return json.load(f)
    if os.path.exists(SYSTEM_CONFIG):
        with open(SYSTEM_CONFIG, encoding='utf-8') as f:
            data = json.load(f)
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
        return data
    raise RuntimeError("No config file found")

EXT_MAP = {
    "png": "image", "jpg": "image", "jpeg": "image", "webp": "image", "avif": "image", "bmp": "image", "tif": "image", "tiff": "image", "tga": "image", "ico": "image", "jfif": "image", "gif": "image", "heic": "image", "heif": "image", "exr": "image", "dds": "image", "psd": "image", "arw": "image", "cr2": "image", "nef": "image", "raf": "image",
    "svg": "svg",
    "mp3": "audio", "flac": "audio", "wav": "audio", "aac": "audio", "ogg": "audio", "oga": "audio", "opus": "audio", "m4a": "audio", "m4b": "audio", "aiff": "audio", "ape": "audio", "wma": "audio", "cda": "audio",
    "mp4": "video", "mkv": "video", "webm": "video", "avi": "video", "mov": "video", "3gp": "video", "3gpp": "video", "flv": "video", "m4v": "video", "mpg": "video", "mpeg": "video", "ogv": "video", "rm": "video", "ts": "video", "vob": "video", "wmv": "video", "bik": "video",
    "pdf": "document", "docx": "document", "doc": "document", "odt": "document", "odp": "document", "ods": "document", "pptx": "document", "ppt": "document", "xlsx": "document", "xls": "document", "txt": "document", "md": "document", "html": "document", "htm": "document",
}

def get_category(filepath):
    ext = os.path.splitext(filepath)[1].lower().lstrip(".")
    if ext in EXT_MAP: return EXT_MAP[ext]
    mime, _ = mimetypes.guess_type(filepath)
    if mime:
        if mime.startswith("image/"): return "svg" if mime == "image/svg+xml" else "image"
        if mime.startswith("video/"): return "video"
        if mime.startswith("audio/"): return "audio"
        if mime in ("application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/markdown", "text/html"): return "document"
    return None

def unique_output(input_file, target_ext):
    base = os.path.splitext(input_file)[0]
    out = f"{base}.{target_ext}"
    if os.path.abspath(out) == os.path.abspath(input_file): out = f"{base}_converted.{target_ext}"
    if os.path.exists(out):
        i = 2
        while os.path.exists(f"{base}_converted_{i}.{target_ext}"): i += 1
        out = f"{base}_converted_{i}.{target_ext}"
    return out

def convert_image(input_file, target_fmt, opts, progress):
    if target_fmt == "svg":
        if opts.get("svg_trace", False) and shutil.which("potrace"):
            out = unique_output(input_file, "svg")
            tmp = input_file + ".__tmp__.pbm"
            try:
                subprocess.run(["magick", input_file, "-colorspace", "Gray", "-threshold", "50%", "-compress", "none", tmp], check=True, capture_output=True)
                subprocess.run(["potrace", tmp, "-s", "-o", out], check=True, capture_output=True)
            finally:
                if os.path.exists(tmp): os.remove(tmp)
            progress(1.0, "Done")
            return out
        import base64
        from PIL import Image
        ext = os.path.splitext(input_file)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif", "bmp": "image/bmp"}.get(ext, "image/png")
        with open(input_file, "rb") as f: data = base64.b64encode(f.read()).decode()
        with Image.open(input_file) as im: w, h = im.size
        out = unique_output(input_file, "svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><image href="data:{mime};base64,{data}" width="{w}" height="{h}"/></svg>')
        progress(1.0, "Done")
        return out

    if target_fmt in ("docx", "odt", "pptx", "xlsx"):
        out = unique_output(input_file, target_fmt)
        if target_fmt == "docx":
            from docx import Document
            from docx.shared import Inches
            doc = Document(); doc.add_picture(input_file, width=Inches(6)); doc.save(out)
        elif target_fmt == "odt":
            from odf.opendocument import OpenDocumentText
            from odf.text import P
            doc = OpenDocumentText(); doc.text.addElement(P(text=os.path.basename(input_file))); doc.save(out)
        elif target_fmt == "pptx":
            from pptx import Presentation
            from pptx.util import Inches
            prs = Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[6]); slide.shapes.add_picture(input_file, Inches(1), Inches(1), width=Inches(8)); prs.save(out)
        elif target_fmt == "xlsx":
            import openpyxl
            from openpyxl.drawing.image import Image as XLImage
            wb = openpyxl.Workbook(); ws = wb.active; ws.add_image(XLImage(input_file), "A1"); wb.save(out)
        progress(1.0, "Done")
        return out

    if target_fmt == "pdf":
        out = unique_output(input_file, "pdf")
        subprocess.run(["magick", input_file, out], check=True, capture_output=True)
        progress(1.0, "Done")
        return out

    out = unique_output(input_file, target_fmt)
    cmd = ["magick", input_file, "-quality", str(opts.get("quality", 95))]
    if target_fmt in ("jpg", "jpeg"): cmd += ["-background", opts.get("background", "#FFFFFF"), "-alpha", "remove", "-alpha", "off"]
    cmd.append(out)
    subprocess.run(cmd, check=True, capture_output=True)
    progress(1.0, "Done")
    return out

def convert_svg(input_file, target_fmt, opts, progress):
    if target_fmt == "svg":
        out = unique_output(input_file, "svg")
        if opts.get("optimize", False) and shutil.which("svgo"): subprocess.run(["svgo", input_file, "-o", out], check=True, capture_output=True)
        else: shutil.copy(input_file, out)
        progress(1.0, "Done")
        return out

    dpi = str(int(opts.get("dpi", 300)))
    out = unique_output(input_file, target_fmt)
    if target_fmt in ("png", "jpg", "jpeg", "webp"):
        tmp_png = f"{input_file}.__tmp__.png"
        try:
            subprocess.run(["rsvg-convert", "-d", dpi, "-p", dpi, "-o", tmp_png, input_file], check=True, capture_output=True)
            if target_fmt == "png": shutil.move(tmp_png, out)
            else:
                cmd = ["magick", tmp_png]
                if target_fmt in ("jpg", "jpeg"): cmd += ["-background", opts.get("background", "#FFFFFF"), "-alpha", "remove", "-alpha", "off"]
                cmd += ["-quality", "95", out]
                subprocess.run(cmd, check=True, capture_output=True)
        finally:
            if os.path.exists(tmp_png): os.remove(tmp_png)
    elif target_fmt == "pdf": subprocess.run(["rsvg-convert", "-f", "pdf", "-o", out, input_file], check=True, capture_output=True)
    else: raise ValueError(f"SVG → {target_fmt} is not supported")
    progress(1.0, "Done")
    return out

def convert_media(input_file, target_fmt, opts, progress, is_video):
    out = unique_output(input_file, target_fmt)
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file], capture_output=True, text=True, timeout=30)
        total = float(probe.stdout.strip())
    except: total = 0.0

    if is_video:
        if target_fmt == "gif": cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"fps={opts.get('fps', 15)},scale={opts.get('width', 480)}:-1:flags=lanczos", "-loop", "0", out]
        elif target_fmt == "webm": cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libvpx-vp9", "-crf", str(opts.get("crf", 30)), "-b:v", "0", "-c:a", "libopus", "-b:a", "128k", out]
        else: cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-crf", str(opts.get("crf", 20)), "-preset", opts.get("preset", "medium"), "-c:a", "aac", "-b:a", "192k", out]
    else:
        bitrate = opts.get("bitrate", "256k")
        if target_fmt == "mp3": cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "libmp3lame", "-b:a", bitrate, out]
        elif target_fmt == "flac": cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "flac", out]
        elif target_fmt == "wav": cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "pcm_s16le", out]
        elif target_fmt in ("ogg", "oga"): cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "libvorbis", "-b:a", bitrate, out]
        elif target_fmt == "opus": cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "libopus", "-b:a", bitrate, out]
        else: cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "aac", "-b:a", bitrate, out]

    cmd = cmd[:1] + ["-progress", "pipe:1", "-nostats", "-hide_banner"] + cmd[1:]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    last_pct = 0
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("out_time_ms=") and total > 0:
            try:
                pct = min(int(int(line.split("=")[1]) / 1_000_000 / total * 100), 99)
                if pct > last_pct: progress(pct / 100.0, f"{pct}%"); last_pct = pct
            except: pass
        elif line == "progress=end": progress(1.0, "Done")
    proc.wait()
    if proc.returncode != 0 or not os.path.exists(out): raise RuntimeError(f"ffmpeg failed (code {proc.returncode})")
    progress(1.0, "Done")
    return out

def document_to_image(input_file, target_fmt, opts, progress):
    dpi, ext, tmpdir = str(int(opts.get("dpi", 150))), os.path.splitext(input_file)[1].lower(), None
    try:
        if ext != ".pdf":
            tmpdir = tempfile.mkdtemp(prefix="snok-")
            subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmpdir, input_file], check=True, capture_output=True, timeout=180)
            pdf_file = os.path.join(tmpdir, os.path.splitext(os.path.basename(input_file))[0] + ".pdf")
            if not os.path.exists(pdf_file): raise RuntimeError("libreoffice did not produce a PDF")
        else: pdf_file = input_file

        base, prefix = os.path.splitext(input_file)[0], f"{os.path.splitext(input_file)[0]}_page"
        fmt = "jpeg" if target_fmt in ("jpg", "jpeg") else "tiff" if target_fmt in ("tif", "tiff") else "png"
        subprocess.run(["pdftoppm", f"-{fmt}", "-r", dpi, pdf_file, prefix], check=True, capture_output=True, timeout=300)

        candidates = sorted([f for f in os.listdir(os.path.dirname(base) or ".") if f.startswith(os.path.basename(prefix)) and f.endswith(f".{fmt if fmt != 'jpeg' else 'jpg'}")])
        if not candidates: raise RuntimeError("pdftoppm did not produce any files")

        first = os.path.join(os.path.dirname(base) or ".", candidates[0])
        out = unique_output(input_file, target_fmt)
        shutil.move(first, out)

        for c in candidates[1:]:
            src = os.path.join(os.path.dirname(base) or ".", c)
            out_p = os.path.splitext(src)[0] + f".{target_fmt}"
            if src != out_p:
                subprocess.run(["magick", src, out_p], capture_output=True)
                try: os.remove(src)
                except: pass
        progress(1.0, f"Done ({len(candidates)} pages)")
        return out
    finally:
        if tmpdir: shutil.rmtree(tmpdir, ignore_errors=True)

def convert_document(input_file, target_fmt, opts, progress):
    ext_in = os.path.splitext(input_file)[1].lower().lstrip(".")
    if ext_in == "pdf":
        out = unique_output(input_file, target_fmt)
        if target_fmt in ("txt", "md", "html"):
            subprocess.run(["pdftotext", "-layout", input_file, out], check=True, capture_output=True)
            progress(1.0, "Done"); return out
        if target_fmt == "docx":
            try:
                from pdf2docx import Converter
                cv = Converter(input_file); cv.convert(out); cv.close()
                progress(1.0, "Done"); return out
            except ImportError: raise RuntimeError("pdf2docx is required")
        raise ValueError(f"PDF → {target_fmt} is not supported")

    if ext_in in ("docx", "doc", "odt", "odp", "ods", "pptx", "ppt", "xlsx", "xls"):
        tmpdir = tempfile.mkdtemp(prefix="snok-")
        try:
            target_lo = target_fmt if target_fmt in ("docx", "doc", "odt", "odp", "ods", "pptx", "ppt", "xlsx", "xls", "pdf") else None
            if not target_lo: raise ValueError(f"Office → {target_fmt} is not supported")
            subprocess.run(["libreoffice", "--headless", "--convert-to", target_lo, "--outdir", tmpdir, input_file], check=True, capture_output=True, timeout=300)
            produced = os.path.join(tmpdir, os.path.splitext(os.path.basename(input_file))[0] + f".{target_lo}")
            if not os.path.exists(produced): raise RuntimeError("libreoffice did not produce a file")
            out = unique_output(input_file, target_fmt)
            shutil.move(produced, out)
            progress(1.0, "Done"); return out
        finally: shutil.rmtree(tmpdir, ignore_errors=True)

    if ext_in in ("txt", "md", "html", "htm") and target_fmt == "pdf":
        out = unique_output(input_file, "pdf")
        if shutil.which("pandoc"):
            subprocess.run(["pandoc", input_file, "-o", out], check=True, capture_output=True, timeout=120)
            progress(1.0, "Done"); return out
        raise RuntimeError("pandoc is required for this conversion")
    raise ValueError(f"{ext_in} → {target_fmt} is not supported")

def build_format_dialog(parent, category, config):
    formats = config.get("formats", {}).get(category, {})
    enabled = [(f, o) for f, o in formats.items() if o.get("enabled", True)]
    if not enabled: return None
    dlg = Gtk.Dialog(title="Snok-Converter — Choose Target Format", transient_for=parent, flags=0)
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
    dlg.set_default_size(360, 420); dlg.set_position(Gtk.WindowPosition.CENTER)
    box = dlg.get_content_area(); box.set_spacing(8); box.set_border_width(12)
    head = Gtk.Label(); head.set_markup(f"<b>Convert {category.upper()} to:</b>"); head.set_xalign(0); box.pack_start(head, False, False, 0)
    scroller = Gtk.ScrolledWindow(); scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scroller.set_min_content_height(220)
    listbox = Gtk.ListBox(); listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    rows = {}
    for i, (f, o) in enumerate(enabled):
        row = Gtk.ListBoxRow(); hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); hbox.set_border_width(6)
        hbox.pack_start(Gtk.Label(label=f.upper()), True, True, 0)
        if o.get("delete_original", False):
            tag = Gtk.Label(); tag.set_markup("<span size='small' foreground='#c0392b'>delete src</span>"); hbox.pack_end(tag, False, False, 0)
        row.add(hbox); listbox.add(row); rows[i] = f
    listbox.select_row(listbox.get_row_at_index(0)); scroller.add(listbox); box.pack_start(scroller, True, True, 0)
    del_chk = Gtk.CheckButton(label="Delete original after conversion"); del_chk.set_active(enabled[0][1].get("delete_original", False)); box.pack_start(del_chk, False, False, 0)
    def on_row_changed(_lb, row):
        if row is None: return
        idx = row.get_index()
        if rows.get(idx): del_chk.set_active(enabled[idx][1].get("delete_original", False))
    listbox.connect("row-selected", on_row_changed); box.show_all()
    return dlg, listbox, rows, del_chk

def run_conversion(files, category, target_fmt, delete_original, parent):
    opts = load_config().get("formats", {}).get(category, {}).get(target_fmt, {})
    win = Gtk.Window(title=f"Converting {len(files)} file(s) → {target_fmt.upper()}")
    win.set_default_size(420, 130); win.set_resizable(False); win.set_keep_above(True); win.set_position(Gtk.WindowPosition.CENTER)
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8); vbox.set_border_width(14); win.add(vbox)
    file_lbl = Gtk.Label(label="Preparing…"); file_lbl.set_xalign(0); file_lbl.set_ellipsize(3); vbox.pack_start(file_lbl, False, False, 0)
    bar = Gtk.ProgressBar(); bar.set_show_text(True); vbox.pack_start(bar, False, False, 0)
    info_lbl = Gtk.Label(label="Elapsed: 0s"); info_lbl.set_xalign(1); vbox.pack_start(info_lbl, False, False, 0)
    win.show_all()
    start = time.time()
    def tick():
        info_lbl.set_text(f"Elapsed: {int(time.time() - start)}s"); return True
    timer = GLib.timeout_add(1000, tick)
    def do_progress(frac, text):
        def upd(): bar.set_fraction(frac); bar.set_text(text)
        GLib.idle_add(upd)
    def worker():
        results, errors = [], []
        for i, f in enumerate(files):
            GLib.idle_add(file_lbl.set_text, f"({i+1}/{len(files)}) {os.path.basename(f)}")
            try:
                if category == "image": out = convert_image(f, target_fmt, opts, do_progress)
                elif category == "svg": out = convert_svg(f, target_fmt, opts, do_progress)
                elif category == "audio": out = convert_media(f, target_fmt, opts, do_progress, False)
                elif category == "video": out = convert_media(f, target_fmt, opts, do_progress, True)
                elif category == "document":
                    if target_fmt in ("png", "jpg", "jpeg", "bmp", "tif", "tiff", "webp"): out = document_to_image(f, target_fmt, opts, do_progress)
                    else: out = convert_document(f, target_fmt, opts, do_progress)
                else: raise RuntimeError(f"Unknown category: {category}")
                results.append(out)
                if delete_original:
                    try:
                        if os.path.abspath(f) != os.path.abspath(out): os.remove(f)
                    except Exception as e: errors.append(f"Delete failed for {f}: {e}")
            except Exception as e: errors.append(f"{os.path.basename(f)}: {e}")
        GLib.idle_add(finish, results, errors)
    def finish(results, errors):
        GLib.source_remove(timer); win.destroy()
        if errors:
            d = Gtk.MessageDialog(transient_for=parent, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=f"Completed with {len(errors)} error(s); {len(results)} succeeded.")
            d.format_secondary_text("\n".join(errors[:8])); d.run(); d.destroy()
        else:
            d = Gtk.MessageDialog(transient_for=parent, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=f"Successfully converted {len(results)} file(s).")
            d.format_secondary_text("\n".join(os.path.basename(r) for r in results[:8])); d.run(); d.destroy()
        Gtk.main_quit()
    threading.Thread(target=worker, daemon=True).start()
    win.connect("destroy", Gtk.main_quit); Gtk.main()

def main():
    files = [f for f in sys.argv[1:] if os.path.isfile(f)]
    if not files: _err("No files were selected."); sys.exit(1)
    try: config = load_config()
    except Exception as e: _err(f"Failed to load config: {e}"); sys.exit(1)
    if not config.get("enabled", True): _err("Snok-Converter is disabled."); sys.exit(0)
    categories = {get_category(f) for f in files}
    if None in categories: _err("Unsupported file type."); sys.exit(1)
    if len(categories) > 1: _err("Please select files of the same type."); sys.exit(1)
    category = categories.pop()
    parent = Gtk.Window(); parent.set_title("Snok-Converter")
    try: parent.set_icon_name(ICON_NAME)
    except: pass
    result = build_format_dialog(parent, category, config)
    if not result: _err("No formats are enabled for this category."); sys.exit(1)
    dlg, listbox, rows, del_chk = result
    response = dlg.run()
    if response != Gtk.ResponseType.OK: dlg.destroy(); sys.exit(0)
    selected = listbox.get_selected_row()
    if selected is None: dlg.destroy(); sys.exit(1)
    idx = selected.get_index(); target_fmt = rows[idx]; delete_original = del_chk.get_active(); dlg.destroy()
    run_conversion(files, category, target_fmt, delete_original, parent)

def _err(msg):
    d = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=msg); d.run(); d.destroy()

if __name__ == "__main__": main()