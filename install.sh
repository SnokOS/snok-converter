#!/usr/bin/env bash
# ============================================================
#  Snok-Converter — System-Wide Installer
#  يُثبّت في /usr/share/snok-converter/ ويجعل الأدوات متاحة لكل المستخدمين
# ============================================================
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "❌ يجب تشغيله كمدير نظام."
    echo "   الاستخدام: sudo bash $0"
    exit 1
fi

# ---------- اكتشاف التوزيعة ----------
DISTRO=""; VERSION=""
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    DISTRO="${ID,,}"; VERSION="${VERSION_ID:-}"
elif [[ -f /etc/arch-release ]]; then DISTRO="arch"
elif [[ -f /etc/debian_version ]]; then
    DISTRO="debian"; VERSION="$(cat /etc/debian_version)"
fi

case "$DISTRO" in
    ubuntu|debian|linuxmint|pop|zorin|kali|elementary|mx|neon)
        FAMILY="debian" ;;
    arch|manjaro|endeavouros|garuda|artix)
        FAMILY="arch" ;;
    fedora|rhel|centos|rocky|almalinux)
        FAMILY="redhat" ;;
    opensuse*|suse*|sles)
        FAMILY="suse" ;;
    *)
        echo "⚠️  توزيعة غير معروفة ($DISTRO) — سأحاول apt"
        FAMILY="debian"
        ;;
esac

echo "==============================================="
echo " Snok-Converter Installer"
echo " التوزيعة: $DISTRO $VERSION   (العائلة: $FAMILY)"
echo "==============================================="
echo ""

# ---------- تثبيت الاعتماديات ----------
echo "📦 تثبيت الاعتماديات…"

install_debian() {
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-gi python3-pil gir1.2-gtk-3.0 \
        imagemagick ffmpeg librsvg2-bin potrace poppler-utils \
        pandoc libreoffice-writer libreoffice-calc libreoffice-impress \
        libheif-examples libavif-bin webp exiftool \
        python3-docx python3-odf python3-pptx python3-openpyxl \
        zenity wget curl || true
    # svgo عبر npm
    if ! command -v svgo >/dev/null 2>&1; then
        echo "  ⏳ تثبيت svgo عبر npm…"
        apt-get install -y nodejs npm >/dev/null 2>&1 || true
        npm install -g svgo >/dev/null 2>&1 || echo "  ⚠️  svgo غير متاح"
    fi
}

install_arch() {
    pacman -Sy --noconfirm --needed \
        python python-gobject python-pillow gtk3 \
        imagemagick ffmpeg librsvg potrace poppler pandoc \
        libreoffice-fresh libheif libavif libwebp perl-image-exiftool \
        python-docx python-odf python-pptx python-openpyxl \
        zenity wget curl nodejs npm || true
    command -v svgo >/dev/null 2>&1 || \
        npm install -g svgo >/dev/null 2>&1 || \
        echo "  ⚠️  svgo غير متاح"
}

install_redhat() {
    dnf install -y --skip-unavailable \
        python3 python3-gobject python3-pillow gtk3 \
        ImageMagick ffmpeg librsvg2-tools potrace poppler-utils \
        pandoc libreoffice-writer libreoffice-calc libreoffice-impress \
        libheif libavif-tools libwebp-tools perl-Image-ExifTool \
        python3-docx python3-odfpy python3-pptx python3-openpyxl \
        zenity wget curl nodejs npm || true
    command -v svgo >/dev/null 2>&1 || \
        npm install -g svgo >/dev/null 2>&1 || true
}

install_suse() {
    zypper --non-interactive install -y \
        python3 python3-gobject python3-Pillow gtk3 \
        ImageMagick ffmpeg librsvg-tools potrace poppler-tools \
        pandoc libreoffice-writer libreoffice-calc libreoffice-impress \
        libheif-tools libavif-tools libwebp-tools perl-Image-ExifTool \
        python3-docx python3-odfpy python3-pptx python3-openpyxl \
        zenity wget curl nodejs npm || true
    command -v svgo >/dev/null 2>&1 || \
        npm install -g svgo >/dev/null 2>&1 || true
}

case "$FAMILY" in
    debian) install_debian ;;
    arch)   install_arch ;;
    redhat) install_redhat ;;
    suse)   install_suse ;;
esac

echo "✅ الاعتماديات جاهزة."
echo ""

# ---------- نسخ الملفات ----------
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="/usr/share/snok-converter"
mkdir -p "$DEST"

echo "📁 نسخ الملفات إلى $DEST…"
for f in snok-convert.py snok-settings.py config.json; do
    if [[ -f "$SRC_DIR/$f" ]]; then
        install -m 0644 "$SRC_DIR/$f" "$DEST/$f"
        echo "  ✓ $f"
    else
        echo "  ⚠️  $f مفقود — تخطي"
    fi
done
chmod 0755 "$DEST/snok-convert.py" "$DEST/snok-settings.py"

# ---------- Wrappers في /usr/bin ----------
echo "🔗 إنشاء Launchers في /usr/bin…"

cat > /usr/bin/snok-settings <<'EOF'
#!/bin/bash
LOG="/tmp/snok-settings.log"
: > "$LOG"
if ! /usr/bin/python3 -c "import gi; gi.require_version('Gtk','3.0')" 2>>"$LOG"; then
    MSG="GTK/PyGObject غير مثبت. ثبّت python3-gi و gir1.2-gtk-3.0"
    command -v zenity >/dev/null && zenity --error --text="$MSG" \
        --title="Snok-Converter" 2>/dev/null
    echo "ERROR: GTK missing" >> "$LOG"
    exit 1
fi
exec /usr/bin/python3 /usr/share/snok-converter/snok-settings.py "$@" \
    >>"$LOG" 2>&1
EOF
chmod 0755 /usr/bin/snok-settings

cat > /usr/bin/snok-convert <<'EOF'
#!/bin/bash
LOG="/tmp/snok-convert.log"
: > "$LOG"
if ! /usr/bin/python3 -c "import gi; gi.require_version('Gtk','3.0')" 2>>"$LOG"; then
    MSG="GTK/PyGObject غير مثبت. ثبّت python3-gi و gir1.2-gtk-3.0"
    command -v zenity >/dev/null && zenity --error --text="$MSG" \
        --title="Snok-Converter" 2>/dev/null
    exit 1
fi
exec /usr/bin/python3 /usr/share/snok-converter/snok-convert.py "$@" \
    >>"$LOG" 2>&1
EOF
chmod 0755 /usr/bin/snok-convert

# ---------- الأيقونة ----------
echo "🎨 تثبيت الأيقونة…"
for SZ in 256 128 64 48 32; do
    mkdir -p "/usr/share/icons/hicolor/${SZ}x${SZ}/apps"
done

if wget -q -O "/tmp/snok-icon.png" \
    "https://avatars.githubusercontent.com/u/135407673?v=4" 2>/dev/null; then
    for SZ in 256 128 64 48 32; do
        cp "/tmp/snok-icon.png" \
           "/usr/share/icons/hicolor/${SZ}x${SZ}/apps/snok-converter.png"
    done
    rm -f /tmp/snok-icon.png
    echo "  ✓ الشعار مثبت"
else
    echo "  ⚠️  فشل تحميل الشعار (تحقق من الاتصال)"
fi
gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true

# ---------- .desktop ----------
echo "📝 ملفات .desktop…"

cat > /usr/share/applications/snok-converter-settings.desktop <<'EOF'
[Desktop Entry]
Type=Application
Version=1.5
Name=Snok-Converter Settings
Name[ar]=إعدادات Snok-Converter
GenericName=File Converter Settings
GenericName[ar]=إعدادات محول الملفات
Comment=Configure Snok-Converter formats and behavior
Comment[ar]=تكوين صيغ وسلوك Snok-Converter
Exec=/usr/bin/snok-settings
TryExec=/usr/bin/snok-settings
Icon=snok-converter
Terminal=false
StartupNotify=true
Categories=XFCE;Settings;X-XFCE-SettingsDialog;Utility;
Keywords=convert;settings;snok;تحويل;إعدادات;
EOF
chmod 0644 /usr/share/applications/snok-converter-settings.desktop

cat > /usr/share/applications/snok-converter.desktop <<'EOF'
[Desktop Entry]
Type=Application
Version=1.5
Name=Snok-Converter
Name[ar]=محول Snok
Comment=Convert files to another format
Comment[ar]=تحويل الملفات إلى صيغ أخرى
Exec=/usr/bin/snok-convert %F
TryExec=/usr/bin/snok-convert
Icon=snok-converter
Terminal=false
StartupNotify=true
Categories=Utility;FileTools;
MimeType=image/png;image/jpeg;image/webp;image/svg+xml;image/avif;image/heic;image/tiff;image/bmp;image/gif;video/mp4;video/x-matroska;video/webm;video/x-msvideo;video/quicktime;audio/mpeg;audio/flac;audio/ogg;audio/x-wav;audio/aac;audio/opus;application/pdf;application/msword;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/vnd.oasis.opendocument.text;application/vnd.ms-excel;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.ms-powerpoint;application/vnd.openxmlformats-officedocument.presentationml.presentation;text/plain;text/markdown;text/html;
EOF
chmod 0644 /usr/share/applications/snok-converter.desktop

update-desktop-database /usr/share/applications 2>/dev/null || true
update-mime-database /usr/share/mime 2>/dev/null || true

# ---------- إعدادات المستخدم + إجراء Thunar ----------
REAL_USER="${SUDO_USER:-}"
if [[ -n "$REAL_USER" && "$REAL_USER" != "root" ]]; then
    REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)
    if [[ -n "$REAL_HOME" && -d "$REAL_HOME" ]]; then
        # config
        mkdir -p "$REAL_HOME/.config/snok-converter"
        if [[ ! -f "$REAL_HOME/.config/snok-converter/config.json" ]]; then
            cp "$DEST/config.json" \
               "$REAL_HOME/.config/snok-converter/config.json"
            chown -R "$REAL_USER:$REAL_USER" \
                  "$REAL_HOME/.config/snok-converter"
            echo "  ✓ config.json نُسخ إلى $REAL_USER"
        fi

        # Thunar custom action
        echo "🔗 إضافة إجراء Thunar لـ $REAL_USER…"
        THUNAR_DIR="$REAL_HOME/.config/Thunar"
        mkdir -p "$THUNAR_DIR"
        chown "$REAL_USER:$REAL_USER" "$THUNAR_DIR"

        python3 - "$REAL_USER" "$THUNAR_DIR" <<'PYEOF'
import sys, os
import xml.etree.ElementTree as ET

user, thunar_dir = sys.argv[1], sys.argv[2]
uca_path = os.path.join(thunar_dir, "uca.xml")

ACTION_NAME = "Snok-Converter"

if os.path.exists(uca_path) and os.path.getsize(uca_path) > 0:
    try:
        tree = ET.parse(uca_path)
        root = tree.getroot()
    except ET.ParseError:
        root = ET.Element("actions")
        tree = ET.ElementTree(root)
else:
    root = ET.Element("actions")
    tree = ET.ElementTree(root)

# تحقق من وجود الإجراء
already = False
for action in root.findall("action"):
    n = action.find("name")
    if n is not None and n.text == ACTION_NAME:
        already = True
        break

if already:
    print("  ℹ️  الإجراء موجود مسبقًا")
else:
    act = ET.SubElement(root, "action")
    ET.SubElement(act, "icon").text = "snok-converter"
    ET.SubElement(act, "name").text = ACTION_NAME
    ET.SubElement(act, "unique-id").text = "snok-converter-001"
    ET.SubElement(act, "command").text = "snok-convert %F"
    ET.SubElement(act, "description").text = "Convert files via Snok-Converter"
    ET.SubElement(act, "patterns").text = "*"
    conds = ET.SubElement(act, "conditions")
    ET.SubElement(conds, "size").text = "1000000000"
    ET.SubElement(conds, "mime-types").text = "*"
    ET.SubElement(conds, "directories").text = ""
    for k in ("audio-files", "image-files",
              "other-files", "text-files", "video-files"):
        ET.SubElement(conds, k).text = "true"

    tree.write(uca_path, encoding="utf-8", xml_declaration=True)
    print("  ✓ إجراء Thunar مضاف")

os.system(f"chown {user}:{user} {uca_path} 2>/dev/null")
PYEOF
    fi
fi

# ---------- ملخص ----------
echo ""
echo "==============================================="
echo " ✅ اكتمل التثبيت بنجاح"
echo "==============================================="
echo ""
echo " 📂 المسار:        $DEST"
echo " 🚀 الأوامر:       snok-settings  |  snok-convert"
echo " ⚙️  الإعدادات:     Settings Manager → Snok-Converter Settings"
echo ""
echo " 🔄 لتفعيل Thunar فورًا:"
echo "    thunar -q && thunar &"
echo ""
echo " 📋 للسجلات:"
echo "    /tmp/snok-settings.log"
echo "    /tmp/snok-convert.log"
echo ""
