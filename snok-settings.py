#!/usr/bin/env python3
"""Snok-Converter Settings GUI."""

import json
import os
import sys

# --- فحص GTK قبل أي شيء آخر ---
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GdkPixbuf
except Exception as e:
    print(f"FATAL: GTK import failed: {e}", file=sys.stderr)
    print("Install: python3-gi gir1.2-gtk-3.0", file=sys.stderr)
    sys.exit(1)


CONFIG_PATH = os.path.expanduser("~/.config/snok-converter/config.json")
SYSTEM_CONFIG = "/usr/share/snok-converter/config.json"
ICON_NAME = "snok-converter"
ICON_FALLBACK = "/usr/share/icons/hicolor/256x256/apps/snok-converter.png"


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"WARN: failed to read user config: {e}", file=sys.stderr)

    if os.path.exists(SYSTEM_CONFIG):
        try:
            with open(SYSTEM_CONFIG, encoding='utf-8') as f:
                data = json.load(f)
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data
        except Exception as e:
            print(f"WARN: failed to seed from system config: {e}", file=sys.stderr)

    return {"version": 2, "enabled": True, "formats": {}}


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


CATEGORY_LABELS = {
    "image":    ("Images",     "🖼️"),
    "svg":      ("SVG",        "🎨"),
    "audio":    ("Audio",      "🎵"),
    "video":    ("Video",      "🎬"),
    "document": ("Documents",  "📄"),
}


class SnokSettings(Gtk.Window):

    def __init__(self):
        super().__init__(title="Snok-Converter Settings")
        self.set_default_size(560, 680)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        try:
            self.set_icon_name(ICON_NAME)
        except Exception:
            if os.path.exists(ICON_FALLBACK):
                try:
                    self.set_icon_from_file(ICON_FALLBACK)
                except Exception:
                    pass

        self.config = load_config()
        self.format_widgets = {}   # {(category, fmt): dict-of-widgets}

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        # --- رأس الصفحة ---
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_FALLBACK, 56, 56, True)
            header.pack_start(Gtk.Image.new_from_pixbuf(pixbuf), False, False, 0)
        except Exception:
            pass

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title_lbl = Gtk.Label()
        title_lbl.set_markup("<span size='x-large' weight='bold'>Snok-Converter</span>")
        title_lbl.set_xalign(0)
        title_box.pack_start(title_lbl, False, False, 0)
        subtitle = Gtk.Label(label="Universal file conversion for Thunar")
        subtitle.set_xalign(0)
        try:
            subtitle.get_style_context().add_class("dim-label")
        except Exception:
            pass
        title_box.pack_start(subtitle, False, False, 0)
        header.pack_start(title_box, False, False, 0)
        main_box.pack_start(header, False, False, 0)

        main_box.pack_start(Gtk.Separator(), False, False, 0)

        # --- مفتاح التشغيل/الإيقاف ---
        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toggle_label = Gtk.Label()
        toggle_label.set_markup("<b>Enable Snok-Converter in Thunar</b>")
        toggle_label.set_xalign(0)
        toggle_box.pack_start(toggle_label, True, True, 0)

        self.enable_switch = Gtk.Switch()
        self.enable_switch.set_active(self.config.get("enabled", True))
        self.enable_switch.connect("state-set", self.on_enable_toggled)
        toggle_box.pack_end(self.enable_switch, False, False, 0)
        main_box.pack_start(toggle_box, False, False, 0)

        # --- دفتر التبويبات ---
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        main_box.pack_start(self.notebook, True, True, 0)

        for cat in ("image", "svg", "audio", "video", "document"):
            if cat not in self.config.get("formats", {}):
                continue
            label, emoji = CATEGORY_LABELS.get(cat, (cat.title(), ""))
            page = self.build_category_page(cat)
            tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            tab.pack_start(Gtk.Label(label=emoji), False, False, 0)
            tab.pack_start(Gtk.Label(label=label), False, False, 0)
            self.notebook.append_page(page, tab)

        # --- شريط الأزرار السفلي ---
        btn_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_bar.set_margin_top(4)

        about_btn = Gtk.Button(label="ℹ️ About")
        about_btn.connect("clicked", self.on_about)
        btn_bar.pack_start(about_btn, False, False, 0)

        reset_btn = Gtk.Button(label="🔄 Reset to Defaults")
        reset_btn.connect("clicked", self.on_reset)
        btn_bar.pack_start(reset_btn, False, False, 0)

        save_btn = Gtk.Button(label="💾 Save")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save)
        btn_bar.pack_end(save_btn, False, False, 0)

        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda *_: Gtk.main_quit())
        btn_bar.pack_end(close_btn, False, False, 0)

        main_box.pack_start(Gtk.Separator(), False, False, 0)
        main_box.pack_start(btn_bar, False, False, 0)

    # -------------------- بناء صفحة الفئة --------------------
    def build_category_page(self, category):
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        outer.set_border_width(8)
        scroller.add(outer)

        formats = self.config.get("formats", {}).get(category, {})
        if not formats:
            outer.pack_start(Gtk.Label(label="(no formats configured)"), False, False, 0)
            return scroller

        # رأس الأعمدة
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        head.set_margin_bottom(4)
        l1 = Gtk.Label(); l1.set_markup("<b>Format</b>"); l1.set_xalign(0); l1.set_size_request(90, -1)
        l2 = Gtk.Label(); l2.set_markup("<b>Show</b>");   l2.set_size_request(60, -1)
        l3 = Gtk.Label(); l3.set_markup("<b>Delete original</b>"); l3.set_xalign(0); l3.set_size_request(150, -1)
        l4 = Gtk.Label(); l4.set_markup("<b>Options</b>"); l4.set_xalign(0)
        head.pack_start(l1, False, False, 0)
        head.pack_start(l2, False, False, 0)
        head.pack_start(l3, False, False, 0)
        head.pack_start(l4, True, True, 0)
        outer.pack_start(head, False, False, 0)
        outer.pack_start(Gtk.Separator(), False, False, 0)

        for fmt, opts in formats.items():
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.set_margin_top(2)
            row.set_margin_bottom(2)

            # اسم الصيغة
            name = Gtk.Label(label=fmt.upper())
            name.set_xalign(0)
            name.set_size_request(90, -1)
            row.pack_start(name, False, False, 0)

            # تفعيل الظهور في القائمة
            show_check = Gtk.CheckButton()
            show_check.set_active(opts.get("enabled", True))
            show_check.set_tooltip_text("Show this format in the right-click menu")
            row.pack_start(show_check, False, False, 0)

            # حذف الأصل
            del_check = Gtk.CheckButton()
            del_check.set_active(opts.get("delete_original", False))
            row.pack_start(del_check, False, False, 0)

            # خيارات إضافية
            extras = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            widgets = {"enabled": show_check, "delete_original": del_check, "extras": {}}

            # جودة للصور
            if fmt in ("jpg", "jpeg", "webp", "avif", "heic", "jfif") or (
                    category == "image" and "quality" in opts):
                lbl = Gtk.Label(label="Q:"); extras.pack_start(lbl, False, False, 0)
                spin = Gtk.SpinButton.new_with_range(1, 100, 1)
                spin.set_value(int(opts.get("quality", 95)))
                extras.pack_start(spin, False, False, 0)
                widgets["extras"]["quality"] = spin

            # DPI للصور النقطية من SVG أو المستندات
            if "dpi" in opts:
                lbl = Gtk.Label(label="DPI:"); extras.pack_start(lbl, False, False, 0)
                spin = Gtk.SpinButton.new_with_range(72, 1200, 1)
                spin.set_value(int(opts.get("dpi", 300)))
                extras.pack_start(spin, False, False, 0)
                widgets["extras"]["dpi"] = spin

            # خلفية JPG
            if fmt in ("jpg", "jpeg") and "background" in opts:
                lbl = Gtk.Label(label="BG:"); extras.pack_start(lbl, False, False, 0)
                entry = Gtk.Entry()
                entry.set_text(opts.get("background", "#FFFFFF"))
                entry.set_width_chars(9)
                extras.pack_start(entry, False, False, 0)
                widgets["extras"]["background"] = entry

            # bitrate للصوت
            if "bitrate" in opts:
                lbl = Gtk.Label(label="kbps:"); extras.pack_start(lbl, False, False, 0)
                spin = Gtk.SpinButton.new_with_range(32, 512, 32)
                b = opts.get("bitrate", "256k")
                try:
                    spin.set_value(int(b.rstrip("kK")))
                except Exception:
                    spin.set_value(256)
                extras.pack_start(spin, False, False, 0)
                widgets["extras"]["bitrate"] = spin

            # CRF للفيديو
            if "crf" in opts:
                lbl = Gtk.Label(label="CRF:"); extras.pack_start(lbl, False, False, 0)
                spin = Gtk.SpinButton.new_with_range(0, 51, 1)
                spin.set_value(int(opts.get("crf", 20)))
                extras.pack_start(spin, False, False, 0)
                widgets["extras"]["crf"] = spin

            # optimize لـ SVG
            if "optimize" in opts:
                chk = Gtk.CheckButton(label="svgo")
                chk.set_active(bool(opts.get("optimize", False)))
                extras.pack_start(chk, False, False, 0)
                widgets["extras"]["optimize"] = chk

            # svg_trace لتحويل صورة إلى SVG
            if "svg_trace" in opts:
                chk = Gtk.CheckButton(label="Trace")
                chk.set_active(bool(opts.get("svg_trace", False)))
                extras.pack_start(chk, False, False, 0)
                widgets["extras"]["svg_trace"] = chk

            row.pack_start(extras, True, True, 0)
            outer.pack_start(row, False, False, 0)

            self.format_widgets[(category, fmt)] = widgets

        return scroller

    # -------------------- معالجات --------------------
    def on_enable_toggled(self, _switch, state):
        self.config["enabled"] = bool(state)
        return False

    def _collect_row(self, category, fmt):
        widgets = self.format_widgets.get((category, fmt))
        if not widgets:
            return
        opts = self.config["formats"][category][fmt]
        opts["enabled"] = widgets["enabled"].get_active()
        opts["delete_original"] = widgets["delete_original"].get_active()
        for key, w in widgets["extras"].items():
            if isinstance(w, Gtk.SpinButton):
                val = int(w.get_value())
                if key == "bitrate":
                    opts[key] = f"{val}k"
                else:
                    opts[key] = val
            elif isinstance(w, Gtk.CheckButton):
                opts[key] = w.get_active()
            elif isinstance(w, Gtk.Entry):
                opts[key] = w.get_text()

    def on_save(self, *_):
        for (cat, fmt) in self.format_widgets.keys():
            self._collect_row(cat, fmt)
        self.config["enabled"] = self.enable_switch.get_active()
        try:
            save_config(self.config)
            self._info("Settings saved successfully.")
        except Exception as e:
            self._error(f"Failed to save settings:\n{e}")

    def on_reset(self, *_):
        dlg = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset all settings to defaults?"
        )
        resp = dlg.run(); dlg.destroy()
        if resp != Gtk.ResponseType.YES:
            return
        try:
            if os.path.exists(SYSTEM_CONFIG):
                with open(SYSTEM_CONFIG, encoding='utf-8') as f:
                    defaults = json.load(f)
                save_config(defaults)
            self._info("Settings reset. Restart the app to see changes.")
        except Exception as e:
            self._error(f"Reset failed:\n{e}")

    def on_about(self, *_):
        dlg = Gtk.AboutDialog(transient_for=self, modal=True)
        dlg.set_program_name("Snok-Converter")
        dlg.set_version("2.0")
        dlg.set_comments("Universal file converter for Thunar\n"
                         "Images · SVG · Audio · Video · Documents")
        dlg.set_website("https://github.com/SnokPC")
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(ICON_FALLBACK)
            dlg.set_logo(pixbuf)
        except Exception:
            pass
        dlg.run(); dlg.destroy()

    def _info(self, msg):
        d = Gtk.MessageDialog(transient_for=self, flags=0,
                              message_type=Gtk.MessageType.INFO,
                              buttons=Gtk.ButtonsType.OK, text=msg)
        d.run(); d.destroy()

    def _error(self, msg):
        d = Gtk.MessageDialog(transient_for=self, flags=0,
                              message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.OK, text=msg)
        d.run(); d.destroy()


def main():
    # تأكد من وجود config المستخدم
    if not os.path.exists(CONFIG_PATH) and os.path.exists(SYSTEM_CONFIG):
        try:
            load_config()  # ينسخ تلقائيًا
        except Exception:
            pass

    win = SnokSettings()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
