# Snok-Converter v2.0
====================
Snok Converter is a very simple tool that allows you to convert and compress files using the context menu in your file manager. It is designed specifically for the system SnokOS linux
====================

تم تصميم واجهة المستخدم لتكون خفيفة قدر الإمكان للحفاظ على سهولة استخدام التطبيق.

يدعم العديد من تنسيقات الملفات المختلفة:

		تنسيقات الإخراج المدعومة			تنسيقات الإدخال المتوافقة
صوتي	صيغ الملفات: flac، aac، ogg، mp3، wav	3gp، 3gpp، aac، aiff، ape، avi، bik، cda، flac، flv، gif، m4v، mkv، mp4، m4a، m4b، mp3، mpg، mpeg، mov، oga، ogg، ogv، opus، rm، ts، vob، wav، webm، wma، wmv
فيديو		webm، mkv، mp4، ogv، avi، gif			3gp، 3gpp، avi، bik، flv، gif، m4v، mkv، mp4، mpg، mpeg، mov، ogv، rm، ts، vob، webm، wmv
صورة	 svg ،png، jpg، ico، webp، avif			arw، avif، bmp، cr2، dds، dns، exr، heic، ico، jfif، jpg، jpeg، nef، png، psd، raf، svg، tif، tiff، tga، webp، pdf، doc*، docx*، odt*، odp*، ods*، ppt*، pptx*، xls*، xlsx*
وثيقة	ملف PDF						doc*، docx*، odt*، odp*، ods*، ppt*، pptx*، xls*، xlsx*، arw، bmp، cr2، dds، dns، exr، heic، ico، jfif، jpg، jpeg، nef، png، psd، raf، svg، tif، tiff، tga، webp

يمكنك تخصيص التطبيق بشكل كبير لإضافة / إزالة إعدادات التحويل المسبقة في قوائم سياق الملفات أو تعديل الإعدادات الموجودة لتغيير خيارات التحويل
====================

طريقة التثبيت
-------------
1. احفظ جميع الملفات في مجلد واحد:
   config.json, snok-settings.py, snok-convert.py, install.sh
2. افتح Terminal في هذا المجلد
3. نفّذ:
   sudo bash install.sh
4. أعد تشغيل Thunar:
   thunar -q && thunar &
5. جرّب الإعدادات:
   snok-settings

طريقة الاستخدام
---------------
- انقر يمين على أي ملف (صورة/فيديو/صوت/مستند/SVG)
- اختر "Snok-Converter"
- اختر الصيغة الهدف من القائمة
- شاهد شريط التقدم
- بعد الانتهاء: نافذة نتيجة + الملف الجديد بجانب الأصلي

الإعدادات
---------
Settings Manager → Snok-Converter Settings

تتيح لك:
- تفعيل/تعطيل الأداة (لتقليل استهلاك الموارد)
- اختيار الصيغ الظاهرة لكل فئة
- تفعيل "حذف الملف الأصلي" لكل صيغة على حدة
- ضبط الجودة (Quality) / DPI / Bitrate / CRF
- تحسين SVG عبر svgo
- تحويل الصور إلى SVG متجهي (Trace)

السجلات
-------
/tmp/snok-settings.log
/tmp/snok-convert.log

إزالة التثبيت
-------------
sudo rm -rf /usr/share/snok-converter \
            /usr/bin/snok-settings \
            /usr/bin/snok-convert \
            /usr/share/applications/snok-converter*.desktop \
            /usr/share/icons/hicolor/*/apps/snok-converter.png
rm -rf ~/.config/snok-converter
# snok-converter
Snok Converter is a very simple tool that allows you to convert and compress files using the context menu in your file manager. It is designed specifically for the system SnokOS linux
