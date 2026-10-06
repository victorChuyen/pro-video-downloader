import os, re, sys, json, glob, subprocess, threading, time, tkinter as tk, urllib.request, webbrowser, shutil
from tkinter import messagebox, filedialog
import customtkinter as ctk
import yt_dlp
from PIL import Image

# --- FFmpeg: dùng bản có sẵn trên máy nếu có, không thì tự dùng bản nhúng kèm theo tool ---
# (nhờ vậy tool chạy được trên MỌI máy, không cần người dùng tự cài FFmpeg riêng)
FFMPEG_PATH = shutil.which('ffmpeg')
if not FFMPEG_PATH:
    try:
        import imageio_ffmpeg
        FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FFMPEG_PATH = None
HAS_FFMPEG = FFMPEG_PATH is not None

# Trình duyệt có thể lấy cookie đăng nhập YouTube từ đó (khắc phục lỗi "Sign in to confirm you're not a bot")
COOKIE_BROWSERS = {
    'Không dùng': None,
    'Chrome': 'chrome',
    'Edge': 'edge',
    'Firefox': 'firefox',
    'Brave': 'brave',
    'Cốc Cốc': 'chrome',  # Cốc Cốc dựa trên Chromium, dùng chung profile format với Chrome
}

DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads', 'VideoDownloader')
HISTORY_FILE = os.path.join(DOWNLOAD_PATH, 'download_history.json')
CONFIG_FILE = os.path.join(os.path.expanduser('~'), 'Downloads', 'VideoDownloader', 'config.json')
if not os.path.exists(DOWNLOAD_PATH): os.makedirs(DOWNLOAD_PATH)

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

PLATFORMS = "YouTube • TikTok • Facebook • Instagram • Twitter/X • Reddit • Vimeo • Dailymotion • Bilibili • Twitch • SoundCloud • 1000+ sites"
DONATE_URL = "https://buymeacoffee.com/victorchuyen"

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return []

def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f: json.dump(data[-500:], f, ensure_ascii=False, indent=2)
    except: pass

# Format khi có ffmpeg: tải riêng video+audio rồi merge → chất lượng cao nhất
_FMT_FFMPEG = {
    "Tốt Nhất (Best)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "4K (2160p)":       "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best",
    "2K (1440p)":       "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best",
    "1080p":            "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
    "720p":             "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
    "480p":             "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
    "Chỉ Lấy Nhạc (MP3)": "bestaudio/best",
    "📝 Chỉ Lấy Script (TXT, Tiếng Anh)": "SCRIPT_ONLY",
}
# Format khi KHÔNG có ffmpeg: chỉ dùng file đã pre-merged (mp4 gộp sẵn)
_FMT_NOFFMPEG = {
    "Tốt Nhất (Best)": "best[ext=mp4]/best[ext=webm]/best",
    "4K (2160p)":       "best[height<=2160][ext=mp4]/best[height<=2160]",
    "2K (1440p)":       "best[height<=1440][ext=mp4]/best[height<=1440]",
    "1080p":            "best[height<=1080][ext=mp4]/best[height<=1080]",
    "720p":             "best[height<=720][ext=mp4]/best[height<=720]",
    "480p":             "best[height<=480][ext=mp4]/best[height<=480]",
    "Chỉ Lấy Nhạc (MP3)": "bestaudio/best",
    "📝 Chỉ Lấy Script (TXT, Tiếng Anh)": "SCRIPT_ONLY",
}
FORMAT_MAP = _FMT_FFMPEG if HAS_FFMPEG else _FMT_NOFFMPEG
SCRIPT_LANGS = ['en', 'en-US', 'en-GB', 'en-orig']  # chỉ lấy phụ đề tiếng Anh

class _StopDownload(Exception):
    """Ném ra từ progress hook khi người dùng bấm nút Dừng, để hủy tải giữa chừng an toàn."""
    pass

def clean_filename(raw, fallback_id="x"):
    if not raw or len(raw) < 3: raw = f"video_{fallback_id}"
    if len(raw) > 150: raw = raw[:150]
    c = re.sub(r'[\\/*?:"<>|]', " ", raw)
    return " ".join(c.split()).strip() or f"video_{fallback_id}"

ERROR_LOG = os.path.join(DOWNLOAD_PATH, 'error.log')
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)  # tránh nháy cửa sổ console khi chạy bản .exe

def log_error(msg):
    try:
        with open(ERROR_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def dedupe_key(url):
    """Khoá chống tải trùng: ID video YouTube nếu có (youtu.be / watch?v= / shorts coi là một), không thì dùng nguyên URL."""
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})', url or '')
    return m.group(1) if m else url

def normalize_channel_url(url):
    """Link kênh YouTube (@name, /channel/, /c/, /user/) mà không chỉ rõ tab thì thêm /videos,
    nếu không yt-dlp trả về danh sách các tab (Videos/Shorts/Live) chứ không phải video."""
    u = url.strip().rstrip('/')
    if re.search(r'youtube\.com/(@[^/]+|channel/[^/]+|c/[^/]+|user/[^/]+)$', u):
        return u + '/videos'
    return u

def flatten_entries(entries):
    out = []
    for e in entries or []:
        if not e: continue
        if e.get('entries'):
            out.extend(flatten_entries(e['entries']))
        else:
            out.append(e)
    return out

def fetch_thumbnail(info, dest_base):
    """Tải thumbnail, thử lần lượt các độ phân giải (maxres có thể 404 với video cũ/Shorts). Trả về đường dẫn file hoặc None."""
    vid_id = info.get('id', '')
    cands = []
    if 'youtube' in (info.get('extractor', '') or '').lower() and vid_id:
        for q in ('maxresdefault', 'sddefault', 'hqdefault'):
            cands.append(f"https://img.youtube.com/vi/{vid_id}/{q}.jpg")
    if info.get('thumbnail'):
        cands.append(info['thumbnail'])
    for t in cands:
        try:
            ext = os.path.splitext(t.split('?')[0])[1].lower()
            if ext not in ('.jpg', '.jpeg', '.png', '.webp'): ext = '.jpg'
            path = dest_base + ext
            urllib.request.urlretrieve(t, path)
            if os.path.getsize(path) > 2000:
                return path
            os.remove(path)
        except Exception as e:
            log_error(f"thumbnail {t}: {e}")
    return None

def write_metadata(info, folder, clean):
    """Xuất metadata (tiêu đề, mô tả, tags, views, thời lượng, ngày đăng...) ra file JSON để nghiên cứu/lên kế hoạch content."""
    keys = ['id', 'title', 'description', 'tags', 'categories', 'view_count', 'like_count', 'comment_count',
            'duration', 'upload_date', 'channel', 'uploader', 'webpage_url', 'license', 'language']
    data = {k: info.get(k) for k in keys}
    with open(os.path.join(folder, f"{clean}_metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class VideoDownloaderApp(ctk.CTk):
    FONT = "Georgia"
    def __init__(self):
        super().__init__()
        self.title("⚡ Pro Video Downloader v2.0 — by VictorChuyen")
        self.geometry("560x780")
        self.minsize(520, 680)
        self.resizable(True, True)
        # Set window icon for titlebar + taskbar
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except: pass
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        cfg = load_config()
        saved_path = cfg.get('download_path', DOWNLOAD_PATH)
        self.download_path = saved_path if os.path.isdir(saved_path) else DOWNLOAD_PATH
        self.history = load_history()
        self._last_hook_time = 0
        self._donate_imgs = None
        self._qr_visible = False
        self._stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nsew")
        self.tabview.add("▶ Tải Video")
        self.tabview.add("⏬ Hàng Loạt")
        self.tabview.add("📡 Quét Kênh")
        self.tabview.add("🖼 Thumbnail")
        self.tabview.add("🕓 Lịch Sử")
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family=self.FONT, size=12, weight="bold"))

        # === TAB 1: SINGLE ===
        t1 = self.tabview.tab("▶ Tải Video")
        t1.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t1, text=f"🌐 {PLATFORMS}", font=ctk.CTkFont(family=self.FONT, size=10),
            text_color="#888", wraplength=460).pack(pady=(12, 4))
        ctk.CTkLabel(t1, text="Dán link video từ bất kỳ nền tảng nào",
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold")).pack(pady=(2, 12))
        uf = ctk.CTkFrame(t1, fg_color="transparent"); uf.pack(pady=(0, 10), fill="x", padx=12)
        self.single_url = ctk.CTkEntry(uf, placeholder_text="https://...", height=46,
            font=ctk.CTkFont(family=self.FONT, size=13))
        self.single_url.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(uf, text="📋", width=46, height=46, command=lambda: self._paste_to(self.single_url),
            font=ctk.CTkFont(size=18), fg_color="#636e72", hover_color="#2d3436").pack(side="right")
        qf = ctk.CTkFrame(t1, fg_color="transparent"); qf.pack(pady=(0, 14))
        ctk.CTkLabel(qf, text="Chất lượng:", font=ctk.CTkFont(family=self.FONT, size=13)).pack(side="left", padx=(0, 10))
        self.q_menu = ctk.CTkOptionMenu(qf, width=210, values=list(FORMAT_MAP.keys()))
        self.q_menu.pack(side="left")
        self.script_var_single = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t1, text="📝 Kèm Script tiếng Anh (.txt)", variable=self.script_var_single,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 8))
        spf1 = ctk.CTkFrame(t1, fg_color="transparent"); spf1.pack(pady=(0, 4))
        self.split_var_single = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(spf1, text="✂️ Cắt video, mỗi đoạn (giây):", variable=self.split_var_single,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(side="left", padx=(0, 8))
        self.split_sec_single = ctk.CTkEntry(spf1, width=64, placeholder_text="60",
            font=ctk.CTkFont(family=self.FONT, size=12))
        self.split_sec_single.pack(side="left")
        self.delete_orig_var_single = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t1, text="🗑 Xoá video gốc sau khi cắt xong", variable=self.delete_orig_var_single,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 10))
        self.btn_single = ctk.CTkButton(t1, text="▶  BẮT ĐẦU TẢI", command=self.on_single, width=230, height=50,
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold"), fg_color="#00b894", hover_color="#00a381")
        self.btn_single.pack(pady=(0, 10))

        # === TAB 2: BULK ===
        t2 = self.tabview.tab("⏬ Hàng Loạt")
        t2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t2, text="Dán danh sách link (mỗi dòng 1 link)",
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold")).pack(pady=(14, 8))
        self.bulk_text = ctk.CTkTextbox(t2, width=480, height=160,
            font=ctk.CTkFont(family=self.FONT, size=12)); self.bulk_text.pack(pady=(0, 10), padx=12)
        self.q_bulk = ctk.CTkOptionMenu(t2, width=210, values=list(FORMAT_MAP.keys()))
        self.q_bulk.pack(pady=(0, 8))
        self.script_var_bulk = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t2, text="📝 Kèm Script tiếng Anh (.txt)", variable=self.script_var_bulk,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 8))
        spf2 = ctk.CTkFrame(t2, fg_color="transparent"); spf2.pack(pady=(0, 4))
        self.split_var_bulk = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(spf2, text="✂️ Cắt video, mỗi đoạn (giây):", variable=self.split_var_bulk,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(side="left", padx=(0, 8))
        self.split_sec_bulk = ctk.CTkEntry(spf2, width=64, placeholder_text="60",
            font=ctk.CTkFont(family=self.FONT, size=12))
        self.split_sec_bulk.pack(side="left")
        self.delete_orig_var_bulk = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t2, text="🗑 Xoá video gốc sau khi cắt xong", variable=self.delete_orig_var_bulk,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 12))
        self.btn_bulk = ctk.CTkButton(t2, text="⏬  TẢI TẤT CẢ", command=self.on_bulk, width=230, height=50,
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold"), fg_color="#00b894", hover_color="#00a381")
        self.btn_bulk.pack(pady=(0, 10))

        # === TAB 3: CHANNEL SCAN ===
        t3 = self.tabview.tab("📡 Quét Kênh")
        t3.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t3, text="Quét & Tải toàn bộ video của Kênh",
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold")).pack(pady=(14, 4))
        ctk.CTkLabel(t3, text="Dán URL kênh YouTube, TikTok profile, hoặc playlist.\nApp sẽ tự quét tất cả video và tải về.",
            font=ctk.CTkFont(family=self.FONT, size=12), text_color="#aaa").pack(pady=(0, 10))
        self.chan_url = ctk.CTkEntry(t3, placeholder_text="https://youtube.com/@ChannelName hoặc playlist URL",
            width=480, height=46, font=ctk.CTkFont(family=self.FONT, size=13))
        self.chan_url.pack(pady=(0, 8), padx=12)
        self.q_chan = ctk.CTkOptionMenu(t3, width=210, values=list(FORMAT_MAP.keys()))
        self.q_chan.pack(pady=(0, 6))
        self.script_var_chan = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t3, text="📝 Kèm Script tiếng Anh (.txt)", variable=self.script_var_chan,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 6))
        spf3 = ctk.CTkFrame(t3, fg_color="transparent"); spf3.pack(pady=(0, 4))
        self.split_var_chan = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(spf3, text="✂️ Cắt video, mỗi đoạn (giây):", variable=self.split_var_chan,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(side="left", padx=(0, 8))
        self.split_sec_chan = ctk.CTkEntry(spf3, width=64, placeholder_text="60",
            font=ctk.CTkFont(family=self.FONT, size=12))
        self.split_sec_chan.pack(side="left")
        self.delete_orig_var_chan = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(t3, text="🗑 Xoá video gốc sau khi cắt xong", variable=self.delete_orig_var_chan,
            font=ctk.CTkFont(family=self.FONT, size=12)).pack(pady=(0, 8))
        cf = ctk.CTkFrame(t3, fg_color="transparent"); cf.pack(pady=(0, 10))
        ctk.CTkLabel(cf, text="Giới hạn:", font=ctk.CTkFont(family=self.FONT, size=13)).pack(side="left", padx=(0, 8))
        self.chan_limit = ctk.CTkOptionMenu(cf, width=150, values=["Tất cả", "10 video", "20 video", "50 video", "100 video"])
        self.chan_limit.pack(side="left")
        bf = ctk.CTkFrame(t3, fg_color="transparent"); bf.pack(pady=(0, 8))
        self.btn_scan = ctk.CTkButton(bf, text="🔍 QUÉT KÊNH", command=self.on_scan, width=155, height=44,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"), fg_color="#6c5ce7", hover_color="#5a4bd1")
        self.btn_scan.pack(side="left", padx=6)
        self.btn_chan_dl = ctk.CTkButton(bf, text="⏬ TẢI TẤT CẢ", command=self.on_chan_download, width=155, height=44,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"), fg_color="#00b894", hover_color="#00a381", state="disabled")
        self.btn_chan_dl.pack(side="left", padx=6)
        self.chan_info = ctk.CTkLabel(t3, text="", font=ctk.CTkFont(family=self.FONT, size=11), text_color="#8cf", wraplength=460)
        self.chan_info.pack(pady=(4, 4))
        self.chan_list = ctk.CTkTextbox(t3, width=480, height=110, state="disabled",
            font=ctk.CTkFont(family=self.FONT, size=11))
        self.chan_list.pack(pady=(0, 6), padx=12)
        self._chan_videos = []

        # === TAB 4: THUMBNAIL ===
        t4 = self.tabview.tab("🖼 Thumbnail")
        t4.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t4, text="Tải Thumbnail chất lượng cao",
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold")).pack(pady=(16, 10))
        self.thumb_url = ctk.CTkEntry(t4, placeholder_text="https://youtube.com/watch?v=...",
            width=480, height=46, font=ctk.CTkFont(family=self.FONT, size=13))
        self.thumb_url.pack(pady=(0, 10), padx=12)
        self.btn_thumb = ctk.CTkButton(t4, text="🖼  TẢI THUMBNAIL", command=self.on_thumb, width=230, height=50,
            font=ctk.CTkFont(family=self.FONT, size=15, weight="bold"), fg_color="#6c5ce7", hover_color="#5a4bd1")
        self.btn_thumb.pack(pady=(0, 6))
        self.thumb_info = ctk.CTkLabel(t4, text="", font=ctk.CTkFont(family=self.FONT, size=11),
            text_color="#8cf", wraplength=460)
        self.thumb_info.pack(pady=(0, 6))
        ctk.CTkLabel(t4, text="─── Tải hàng loạt thumbnail ───",
            text_color="#555", font=ctk.CTkFont(family=self.FONT, size=11)).pack(pady=(8, 8))
        self.thumb_bulk = ctk.CTkTextbox(t4, width=480, height=90,
            font=ctk.CTkFont(family=self.FONT, size=12)); self.thumb_bulk.pack(pady=(0, 10), padx=12)
        self.btn_thumb_bulk = ctk.CTkButton(t4, text="🖼  TẢI TẤT CẢ THUMBNAIL", command=self.on_thumb_bulk,
            width=230, height=42, font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"),
            fg_color="#6c5ce7", hover_color="#5a4bd1")
        self.btn_thumb_bulk.pack(pady=(0, 8))

        # === TAB 5: HISTORY ===
        t5 = self.tabview.tab("🕓 Lịch Sử")
        t5.grid_columnconfigure(0, weight=1)
        hh = ctk.CTkFrame(t5, fg_color="transparent"); hh.pack(fill="x", pady=(12, 8), padx=12)
        self.hist_count = ctk.CTkLabel(hh, text=f"📊 Đã tải: {len(self.history)} video",
            font=ctk.CTkFont(family=self.FONT, size=14, weight="bold"))
        self.hist_count.pack(side="left")
        ctk.CTkButton(hh, text="🗑 Xóa", width=76, height=32, fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(family=self.FONT, size=12), command=self.clear_history).pack(side="right")
        self.hist_text = ctk.CTkTextbox(t5, width=480, height=310, state="disabled",
            font=ctk.CTkFont(family=self.FONT, size=12))
        self.hist_text.pack(pady=(0, 8), padx=12)
        self._refresh_hist()

        # === STATUS BAR ===
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, padx=16, pady=(0, 6), sticky="ew"); sf.grid_columnconfigure(0, weight=1)
        self.pbar = ctk.CTkProgressBar(sf, width=490); self.pbar.set(0)
        self.pbar.grid(row=0, column=0, pady=(6, 2)); self.pbar.grid_remove()
        self.status = ctk.CTkLabel(sf, text="Sẵn sàng", font=ctk.CTkFont(family=self.FONT, size=13))
        self.status.grid(row=1, column=0, pady=(2, 6))
        fbf = ctk.CTkFrame(sf, fg_color="transparent"); fbf.grid(row=2, column=0, pady=(0, 4))
        ctk.CTkButton(fbf, text="📂  MỞ THƯ MỤC", command=lambda: os.startfile(self.download_path),
            fg_color="#2ecc71", hover_color="#27ae60", width=196, height=38,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(fbf, text="📁  ĐỔI THƯ MỤC", command=self._pick_folder,
            fg_color="#636e72", hover_color="#2d3436", width=196, height=38,
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold")).pack(side="left")
        cbf = ctk.CTkFrame(sf, fg_color="transparent"); cbf.grid(row=5, column=0, pady=(2, 2))
        ctk.CTkLabel(cbf, text="🍪 Cookie trình duyệt:",
            font=ctk.CTkFont(family=self.FONT, size=11), text_color="#aaa").pack(side="left", padx=(0, 8))
        self.cookie_browser = ctk.CTkOptionMenu(cbf, width=140, height=30,
            values=list(COOKIE_BROWSERS.keys()), command=self._on_cookie_browser_change,
            font=ctk.CTkFont(family=self.FONT, size=11))
        saved_browser = load_config().get('cookie_browser', 'Không dùng')
        self.cookie_browser.set(saved_browser if saved_browser in COOKIE_BROWSERS else 'Không dùng')
        self.cookie_browser.pack(side="left")
        ctk.CTkLabel(cbf, text="  ⚠ Chrome/Edge hay lỗi do khóa mã hóa mới, khuyên dùng Firefox",
            font=ctk.CTkFont(family=self.FONT, size=9), text_color="#e67e22").pack(side="left", padx=(6, 0))

        cff = ctk.CTkFrame(sf, fg_color="transparent"); cff.grid(row=6, column=0, pady=(2, 2))
        self.cookies_file_path = load_config().get('cookies_file', '')
        cookie_file_label_text = f"📄 File: ...{self.cookies_file_path[-30:]}" if self.cookies_file_path else "📄 Chưa chọn file cookies.txt"
        self.cookies_file_label = ctk.CTkLabel(cff, text=cookie_file_label_text,
            font=ctk.CTkFont(family=self.FONT, size=10), text_color="#77dd77" if self.cookies_file_path else "#777")
        self.cookies_file_label.pack(side="left", padx=(0, 8))
        ctk.CTkButton(cff, text="📁 Chọn cookies.txt (khuyên dùng)", command=self._pick_cookies_file,
            width=210, height=28, fg_color="#0984e3", hover_color="#0765ad",
            font=ctk.CTkFont(family=self.FONT, size=10)).pack(side="left")
        self.btn_clear_cookies = ctk.CTkButton(cff, text="✕", command=self._clear_cookies_file, width=28, height=28,
            fg_color="#636e72", hover_color="#2d3436")
        if self.cookies_file_path:
            self.btn_clear_cookies.pack(side="left", padx=(6, 0))
        uf2 = ctk.CTkFrame(sf, fg_color="transparent"); uf2.grid(row=7, column=0, pady=(2, 2))
        try:
            ver = yt_dlp.version.__version__
        except Exception:
            ver = "?"
        self.ytdlp_label = ctk.CTkLabel(uf2, text=f"yt-dlp {ver}", font=ctk.CTkFont(family=self.FONT, size=10), text_color="#777")
        self.ytdlp_label.pack(side="left", padx=(0, 8))
        ctk.CTkButton(uf2, text="⟳ Cập nhật yt-dlp", command=self._update_ytdlp, width=130, height=24,
            fg_color="#636e72", hover_color="#2d3436", font=ctk.CTkFont(family=self.FONT, size=10)).pack(side="left")
        self.btn_stop = ctk.CTkButton(sf, text="⏹  DỪNG TẢI", command=self._request_stop,
            fg_color="#e74c3c", hover_color="#c0392b", width=196, height=36, state="disabled",
            font=ctk.CTkFont(family=self.FONT, size=13, weight="bold"))
        self.btn_stop.grid(row=4, column=0, pady=(2, 4))
        self.path_label = ctk.CTkLabel(sf, text=f"📍 {self.download_path}",
            font=ctk.CTkFont(family=self.FONT, size=10), text_color="#777", wraplength=490)
        self.path_label.grid(row=3, column=0, pady=(0, 4))

        # === COFFEE FOOTER with hover QR ===
        self._build_coffee_footer()

    # ===== FOLDER PICKER =====
    def _ydl_extra_opts(self):
        """Các option dùng chung cho mọi lần gọi yt-dlp: đường dẫn FFmpeg (đã nhúng sẵn trong tool),
        cookie (ưu tiên file cookies.txt nếu có), và giả lập client Android/TV của YouTube — client này
        thường không bị đòi PO token/bot-check gắt như client web, hay giúp qua được lỗi 'Sign in to confirm'."""
        extra = {
            # Dùng player_client mặc định của yt-dlp (client android hay cần PO token → lỗi 403)
        }
        if HAS_FFMPEG and FFMPEG_PATH:
            extra['ffmpeg_location'] = FFMPEG_PATH
        cookies_file = getattr(self, 'cookies_file_path', '') or load_config().get('cookies_file', '')
        if cookies_file and os.path.exists(cookies_file):
            extra['cookiefile'] = cookies_file
            return extra  # Có file cookies.txt thì dùng luôn, không cần đọc từ trình duyệt nữa
        try:
            choice = self.cookie_browser.get()
        except Exception:
            choice = load_config().get('cookie_browser', 'Không dùng')
        browser_key = COOKIE_BROWSERS.get(choice)
        if browser_key:
            extra['cookiesfrombrowser'] = (browser_key,)
        return extra

    def _pick_cookies_file(self):
        path = filedialog.askopenfilename(title="Chọn file cookies.txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.cookies_file_path = path
            cfg = load_config(); cfg['cookies_file'] = path; cfg['download_path'] = self.download_path
            save_config(cfg)
            self.cookies_file_label.configure(text=f"📄 File: ...{path[-30:]}", text_color="#77dd77")
            self.btn_clear_cookies.pack(side="left", padx=(6, 0))
            messagebox.showinfo("Đã chọn", "Đã lưu file cookies.txt.")

    def _clear_cookies_file(self):
        self.cookies_file_path = ''
        cfg = load_config(); cfg['cookies_file'] = ''; cfg['download_path'] = self.download_path
        save_config(cfg)
        self.cookies_file_label.configure(text="📄 Chưa chọn file cookies.txt", text_color="#777")
        self.btn_clear_cookies.pack_forget()

    def _update_ytdlp(self):
        """Cập nhật yt-dlp (YouTube đổi liên tục nên bản cũ hay hỏng). Bản .exe đóng gói không tự cập nhật được."""
        if getattr(sys, 'frozen', False):
            messagebox.showinfo("Cập nhật", "Bản .exe đã đóng gói sẵn yt-dlp. Để cập nhật, chạy lại build.bat (tự lấy yt-dlp mới nhất) hoặc chạy từ source: pip install -U yt-dlp")
            return
        self.status.configure(text="⟳ Đang cập nhật yt-dlp...", text_color="white")
        def work():
            try:
                r = subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                                   capture_output=True, text=True, creationflags=NO_WINDOW)
                ok = r.returncode == 0
                msg = "✅ Đã cập nhật yt-dlp. Khởi động lại app để áp dụng." if ok else "❌ Cập nhật thất bại"
                if not ok: log_error(f"update yt-dlp: {r.stderr[-300:]}")
            except Exception as e:
                msg = f"❌ Cập nhật thất bại: {str(e)[:60]}"
                log_error(f"update yt-dlp: {e}")
            self.after(0, lambda: self.status.configure(text=msg))
        threading.Thread(target=work, daemon=True).start()

    def _on_cookie_browser_change(self, choice):
        cfg = load_config()
        cfg['cookie_browser'] = choice
        cfg['download_path'] = self.download_path
        save_config(cfg)

    def _pick_folder(self):
        chosen = filedialog.askdirectory(title="Chọn thư mục lưu video", initialdir=self.download_path)
        if chosen:
            self.download_path = os.path.normpath(chosen)
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            self.path_label.configure(text=f"📍 {self.download_path}")
            cfg = load_config(); cfg['download_path'] = self.download_path
            save_config(cfg)

    # ===== HISTORY =====
    def _refresh_hist(self):
        self.hist_text.configure(state="normal"); self.hist_text.delete("1.0", "end")
        if not self.history:
            self.hist_text.insert("1.0", "Chưa có video nào. Hãy tải video đầu tiên! 🎬")
        else:
            lines = []
            for i, h in enumerate(reversed(self.history[-100:]), 1):
                lines.append(f"{i}. {h.get('title','N/A')}\n   🔗 {h.get('url','')[:60]}...\n   📅 {h.get('time','')}  •  📁 {h.get('type','video')}")
            self.hist_text.insert("1.0", "\n\n".join(lines))
        self.hist_text.configure(state="disabled")
        self.hist_count.configure(text=f"📊 Đã tải: {len(self.history)} video")

    def clear_history(self):
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ lịch sử?"):
            self.history = []; save_history([]); self._refresh_hist()

    # ===== CHANNEL SCAN =====
    def on_scan(self):
        url = self.chan_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập URL kênh!"); return
        self.btn_scan.configure(state="disabled"); self.chan_info.configure(text="🔍 Đang quét kênh...")
        self.chan_list.configure(state="normal"); self.chan_list.delete("1.0", "end"); self.chan_list.configure(state="disabled")
        threading.Thread(target=self._scan_worker, args=(url,), daemon=True).start()

    def _get_limit(self):
        v = self.chan_limit.get()
        if v == "Tất cả": return None
        return int(v.split()[0])

    def _scan_worker(self, url):
        try:
            limit = self._get_limit()
            opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'skip_download': True}
            opts.update(self._ydl_extra_opts())
            if limit: opts['playlistend'] = limit
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(normalize_channel_url(url), download=False)
            entries = flatten_entries(info.get('entries', []))
            if not entries and info.get('id'):
                entries = [info]
            if limit: entries = entries[:limit]

            # Link đã tải thành công trước đó (từ lịch sử) để loại trừ ngay khi quét
            downloaded_urls = {dedupe_key(h.get('url')) for h in self.history if h.get('url') and h.get('type') != 'thumbnail'}

            all_videos = []
            for e in entries:
                if e:
                    vurl = e.get('url') or e.get('webpage_url', '')
                    if vurl and not vurl.startswith('http') and e.get('id'):
                        vurl = f"https://www.youtube.com/watch?v={e['id']}"
                    all_videos.append({'url': vurl, 'title': e.get('title', 'N/A')})
            total_found = len(all_videos)
            self._chan_videos = [v for v in all_videos if dedupe_key(v['url']) not in downloaded_urls]
            n = len(self._chan_videos)
            n_skipped = total_found - n

            channel = info.get('channel', '') or info.get('uploader', '') or info.get('title', 'Kênh')
            skip_note = f" (đã bỏ qua {n_skipped} video có trong lịch sử)" if n_skipped > 0 else ""
            if n > 0:
                msg = f"✅ Tìm thấy {n} video mới trong kênh: {channel}{skip_note}"
            else:
                msg = f"ℹ️ Không có video mới — cả {total_found} video trong kênh đều đã có trong lịch sử."
            self.after(0, lambda m=msg: self.chan_info.configure(text=m))
            self.after(0, lambda: self.btn_scan.configure(state="normal"))
            self.after(0, lambda: self.btn_chan_dl.configure(state=("normal" if n > 0 else "disabled")))
            # Show list (chỉ video mới)
            lines = [f"{i+1}. {v['title']}" for i, v in enumerate(self._chan_videos[:100])]
            txt = "\n".join(lines) if lines else "Không có video mới nào."
            if n > 100: txt += f"\n... và {n-100} video khác"
            self.after(0, lambda: (self.chan_list.configure(state="normal"), self.chan_list.delete("1.0","end"), self.chan_list.insert("1.0", txt), self.chan_list.configure(state="disabled")))
        except Exception as e:
            self.after(0, lambda: self.chan_info.configure(text=f"❌ Lỗi: {str(e)[:80]}"))
            self.after(0, lambda: self.btn_scan.configure(state="normal"))

    def _get_split_seconds(self, entry_widget):
        """Đọc và kiểm tra số giây người dùng nhập để cắt video. Trả về None nếu không hợp lệ."""
        txt = entry_widget.get().strip()
        try:
            v = int(txt)
            return v if v > 0 else None
        except Exception:
            return None

    def _validate_split(self, want_split, split_entry):
        """Kiểm tra điều kiện cắt video trước khi bắt đầu tải. Trả về (ok, split_seconds)."""
        if not want_split:
            return True, 0
        if not HAS_FFMPEG:
            messagebox.showerror("Lỗi", "Cần cài FFmpeg để dùng chức năng cắt video!")
            return False, 0
        split_sec = self._get_split_seconds(split_entry)
        if not split_sec:
            messagebox.showerror("Lỗi", "Nhập số giây hợp lệ (số nguyên > 0) để cắt video!")
            return False, 0
        return True, split_sec

    def on_chan_download(self):
        if not self._chan_videos: messagebox.showerror("Lỗi", "Quét kênh trước!"); return
        ok, split_sec = self._validate_split(self.split_var_chan.get(), self.split_sec_chan)
        if not ok: return
        urls = [v['url'] for v in self._chan_videos if v['url']]
        q = self.q_chan.get()
        self.btn_chan_dl.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=(urls, q, True, self.script_var_chan.get(),
            self.split_var_chan.get(), split_sec, self.delete_orig_var_chan.get()), daemon=True).start()

    # ===== DOWNLOADS =====
    def on_single(self):
        url = self.single_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập link!"); return
        ok, split_sec = self._validate_split(self.split_var_single.get(), self.split_sec_single)
        if not ok: return
        self.btn_single.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=([url], self.q_menu.get(), False, self.script_var_single.get(),
            self.split_var_single.get(), split_sec, self.delete_orig_var_single.get()), daemon=True).start()

    def on_bulk(self):
        txt = self.bulk_text.get("1.0", "end").strip()
        if not txt: messagebox.showerror("Lỗi", "Dán link!"); return
        ok, split_sec = self._validate_split(self.split_var_bulk.get(), self.split_sec_bulk)
        if not ok: return
        urls = [u.strip() for u in txt.split('\n') if u.strip()]
        self.btn_bulk.configure(state="disabled")
        threading.Thread(target=self._download_engine, args=(urls, self.q_bulk.get(), False, self.script_var_bulk.get(),
            self.split_var_bulk.get(), split_sec, self.delete_orig_var_bulk.get()), daemon=True).start()

    def _paste_to(self, entry):
        """Quick-paste clipboard content into an entry field."""
        try:
            clip = self.clipboard_get()
            if clip:
                entry.delete(0, "end")
                entry.insert(0, clip.strip())
        except: pass

    def _download_engine(self, urls, quality, is_channel=False, want_script=False,
                          want_split=False, split_seconds=0, delete_original=False):
        total = len(urls); ok = 0; skipped = 0; failures = []
        fmt = FORMAT_MAP.get(quality, "bestvideo+bestaudio/best")
        is_mp3 = quality == "Chỉ Lấy Nhạc (MP3)"
        is_script_only = fmt == "SCRIPT_ONLY"
        if is_script_only:
            want_script = True  # chế độ này bắt buộc phải lấy script
        ydl_opts = {
            'quiet': True, 'no_warnings': True,
            'progress_hooks': [self._hook], 'noplaylist': True,
            'concurrent_fragment_downloads': 8, 'retries': 5, 'fragment_retries': 5,
            'http_chunk_size': 10485760,
            'socket_timeout': 30,
            'noprogress': True,
        }
        ydl_opts.update(self._ydl_extra_opts())
        if is_script_only:
            # Không tải video/audio, chỉ lấy phụ đề để dựng script
            ydl_opts['skip_download'] = True
        else:
            ydl_opts['format'] = fmt
            if HAS_FFMPEG:
                ydl_opts['merge_output_format'] = 'mp4'
            if is_mp3:
                if HAS_FFMPEG:
                    ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
                    ydl_opts.pop('merge_output_format', None)
                else:
                    ydl_opts['format'] = 'bestaudio/best'
        if want_script:
            # Lấy phụ đề (ưu tiên có sẵn, không có thì lấy phụ đề tự động)
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = SCRIPT_LANGS
            ydl_opts['subtitlesformat'] = 'srt/vtt/best'
            if HAS_FFMPEG:
                ydl_opts.setdefault('postprocessors', []).append(
                    {'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'})
        # Danh sách link đã tải thành công trước đó (lấy từ lịch sử) để loại trừ, không cần dò mạng
        downloaded_urls = {dedupe_key(h.get('url')) for h in self.history if h.get('url') and h.get('type') != 'thumbnail'}

        self.after(0, lambda: (self.pbar.grid(), self.pbar.set(0)))
        self._stop_event.clear()
        self.after(0, lambda: self.btn_stop.configure(state="normal"))
        stopped = False
        # Reuse single yt-dlp instance for entire batch
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(urls):
                if self._stop_event.is_set():
                    stopped = True
                    break
                try:
                    # --- Kiểm tra trong lịch sử: đã tải link này rồi thì bỏ qua ---
                    if dedupe_key(url) in downloaded_urls:
                        skipped += 1
                        self.after(0, lambda idx=i+1, u=url: self.status.configure(
                            text=f"[{idx}/{total}] ⏭ Đã có trong lịch sử — bỏ qua: {u[:40]}", text_color="#f1c40f"))
                        continue

                    self.after(0, lambda idx=i+1, u=url: self.status.configure(
                        text=f"[{idx}/{total}] Đang tải: {u[:50]}...", text_color="white"))
                    tmp_base = f"_tmp_{threading.get_ident()}_{i}"
                    tmp = os.path.join(self.download_path, f"{tmp_base}.%(ext)s")
                    ydl.params['outtmpl'] = {'default': tmp}
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        failures.append((url, "Không lấy được thông tin video"))
                        continue
                    raw = info.get('fulltitle') or info.get('title') or ''
                    if len(raw) < 5:
                        d = info.get('description', '')
                        if d: raw = d.split('\n')[0]
                    if not raw: raw = info.get('alt_title') or 'video'
                    clean = clean_filename(raw, info.get('id', 'x'))

                    if is_script_only:
                        # Chế độ chỉ lấy script/phụ đề: không có file video
                        folder = os.path.join(self.download_path, clean)
                        c = 1
                        while os.path.exists(folder) and os.listdir(folder):
                            folder = os.path.join(self.download_path, f"{clean} ({c})"); c += 1
                        os.makedirs(folder, exist_ok=True)
                        got_script = self._save_script_files(tmp_base, folder, clean)
                        if got_script:
                            ok += 1
                            self.history.append({"url": url, "title": clean, "type": "script", "time": time.strftime("%Y-%m-%d %H:%M"), "folder": folder})
                            downloaded_urls.add(dedupe_key(url))
                        else:
                            failures.append((url, "Video không có phụ đề/script khả dụng"))
                            if not os.listdir(folder):
                                try: os.rmdir(folder)
                                except Exception: pass
                        continue

                    src = ydl.prepare_filename(info)
                    if is_mp3:
                        mp3 = os.path.splitext(src)[0] + ".mp3"
                        if os.path.exists(mp3): src = mp3
                    ext = os.path.splitext(src)[1]

                    if os.path.exists(src):
                        # Kiểm tra lại lần nữa phòng trường hợp thư mục đã được tạo bởi 1 video khác
                        # trùng tên trong cùng đợt tải này (tên trùng thì thêm số vào sau)
                        folder = os.path.join(self.download_path, clean)
                        c = 1
                        while os.path.exists(folder) and os.listdir(folder):
                            folder = os.path.join(self.download_path, f"{clean} ({c})"); c += 1
                        os.makedirs(folder, exist_ok=True)

                        dst = os.path.join(folder, f"{clean}{ext}")
                        os.rename(src, dst); ok += 1

                        # Tải kèm thumbnail (có fallback độ phân giải) + metadata vào chung thư mục với video
                        try:
                            fetch_thumbnail(info, os.path.join(folder, f"{clean}_thumb"))
                        except Exception as e:
                            log_error(f"thumb {url}: {e}")
                        try:
                            write_metadata(info, folder, clean)
                        except Exception as e:
                            log_error(f"metadata {url}: {e}")

                        # Kèm script/phụ đề (nếu người dùng bật tuỳ chọn) vào chung thư mục với video
                        if want_script:
                            try:
                                self._save_script_files(tmp_base, folder, clean)
                            except Exception:
                                pass  # Không có phụ đề cũng không sao, video vẫn tính là thành công

                        # Cắt video thành nhiều đoạn nhỏ (nếu người dùng bật tuỳ chọn) — chỉ áp dụng
                        # cho file video thật, không áp dụng cho MP3
                        if want_split and not is_mp3 and split_seconds > 0:
                            self.after(0, lambda idx=i+1: self.status.configure(
                                text=f"[{idx}/{total}] ✂️ Đang cắt video...", text_color="white"))
                            try:
                                if not self._split_video(dst, folder, clean, ext, split_seconds, delete_original):
                                    log_error(f"split failed: {dst}")
                                    self.after(0, lambda: self.status.configure(text="⚠ Cắt video thất bại (giữ video gốc)", text_color="#f1c40f"))
                            except Exception as e:
                                log_error(f"split {dst}: {e}")

                        self.history.append({"url": url, "title": clean, "type": "mp3" if is_mp3 else "video", "time": time.strftime("%Y-%m-%d %H:%M"), "folder": folder})
                        downloaded_urls.add(dedupe_key(url))  # Cập nhật để tránh tải trùng nếu link lặp lại trong cùng đợt này
                    else:
                        failures.append((url, "File không tồn tại sau khi tải"))
                except _StopDownload:
                    stopped = True
                    # Dọn các file tạm dở dang của video đang tải khi bị dừng
                    try:
                        for leftover in glob.glob(os.path.join(self.download_path, f"{tmp_base}.*")):
                            os.remove(leftover)
                    except Exception:
                        pass
                    self.after(0, lambda: self.status.configure(text="⏹ Đã dừng tải", text_color="#f1c40f"))
                    break
                except Exception as e:
                    err_short = str(e).split('\n')[0][:120]
                    failures.append((url, err_short))
                    self.after(0, lambda err=err_short: self.status.configure(
                        text=f"❌ {err[:70]}", text_color="#ff7675"))
        # Batch save history once
        save_history(self.history)
        self._stop_event.clear()
        self.after(0, lambda: self.btn_stop.configure(state="disabled"))
        self.after(0, lambda: self._finish(ok, total, is_channel, failures, skipped, stopped))

    def _finish(self, ok, total, is_channel=False, failures=None, skipped=0, stopped=False):
        failures = failures or []
        self.btn_single.configure(state="normal"); self.btn_bulk.configure(state="normal"); self.btn_chan_dl.configure(state="normal")
        self.pbar.set(1.0 if ok > 0 else 0)
        if stopped:
            self.status.configure(text=f"⏹ Đã dừng — hoàn thành {ok}/{total} trước khi dừng", text_color="#f1c40f")
        else:
            self.status.configure(text=f"✅ Thành công {ok}/{total} (⏭ bỏ qua {skipped})" if ok > 0 or skipped > 0 else f"❌ Thất bại {total}/{total}", text_color="white")
        self._refresh_hist()
        skip_note = f"\n⏭ Bỏ qua (đã tải trước đó): {skipped}" if skipped > 0 else ""
        if stopped:
            messagebox.showinfo("Đã dừng", f"⏹ Đã dừng tải theo yêu cầu.\n✅ Hoàn thành: {ok}/{total}{skip_note}\n📁 {self.download_path}")
        elif ok > 0 and not failures:
            messagebox.showinfo("Kết quả", f"✅ Đã tải {ok}/{total} {'video từ kênh' if is_channel else 'video'} (kèm thumbnail, mỗi video 1 thư mục riêng).{skip_note}\n📁 {self.download_path}")
        elif ok > 0 and failures:
            detail = "\n".join([f"❌ {u[:60]}\n   ↳ {e[:80]}" for u, e in failures[:8]])
            if len(failures) > 8: detail += f"\n... và {len(failures)-8} link khác thất bại"
            messagebox.showwarning("Kết quả", f"✅ Thành công: {ok}/{total}{skip_note}\n❌ Thất bại: {len(failures)}\n\n{detail}")
        elif failures and skipped > 0 and ok == 0:
            detail = "\n".join([f"❌ {u[:60]}\n   ↳ {e[:80]}" for u, e in failures[:6]])
            if len(failures) > 6: detail += f"\n... và {len(failures)-6} link khác"
            messagebox.showwarning("Kết quả", f"{skip_note}\n❌ Thất bại: {len(failures)}\n\n{detail}")
        elif failures:
            detail = "\n".join([f"❌ {u[:60]}\n   ↳ {e[:80]}" for u, e in failures[:6]])
            if len(failures) > 6: detail += f"\n... và {len(failures)-6} link khác"
            messagebox.showerror("Thất bại", f"Không tải được {total} video.\n\n{detail}\n\n💡 Kiểm tra lại link hoặc kết nối mạng.")
        elif skipped > 0 and total == skipped:
            messagebox.showinfo("Kết quả", f"⏭ Cả {skipped} video đều đã có trong lịch sử tải trước đó, không có video mới nào để tải.")
        elif total > 0:
            messagebox.showerror("Thất bại", "Không tải được video.\n💡 Kiểm tra link hoặc kết nối mạng.")

    def _request_stop(self):
        """Người dùng bấm nút Dừng: đặt cờ để _hook ném lỗi hủy tải ở lần callback tiếp theo."""
        self._stop_event.set()
        self.btn_stop.configure(state="disabled")
        self.status.configure(text="⏹ Đang dừng, vui lòng đợi...", text_color="#f1c40f")

    def _hook(self, d):
        if self._stop_event.is_set():
            raise _StopDownload("Người dùng đã dừng tải")
        if d['status'] == 'downloading':
            now = time.time()
            if now - self._last_hook_time < 0.25: return
            self._last_hook_time = now
            try:
                done = d.get('downloaded_bytes') or 0
                tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                p = min(done / tot, 1.0) if tot else 0
                spd = d.get('speed'); eta = d.get('eta')
                spd_s = f"{spd/1048576:.1f} MB/s" if spd else ""
                eta_s = f"{int(eta)}s" if eta is not None else ""
                self.after(0, lambda: self.pbar.set(p))
                self.after(0, lambda: self.status.configure(text=f"Đang tải: {p*100:.0f}% — {spd_s} — ETA: {eta_s}"))
            except Exception: pass
        elif d['status'] == 'finished':
            self.after(0, lambda: (self.pbar.set(0.95), self.status.configure(text="Đang hoàn thiện...")))

    # ===== SCRIPT / PHỤ ĐỀ =====
    # ===== CẮT VIDEO =====
    def _split_video(self, src_path, folder, clean, ext, split_seconds, delete_original):
        """Dùng ffmpeg cắt `src_path` thành nhiều đoạn `split_seconds` giây (cắt nhanh,
        không re-encode nên có thể lệch vài giây theo keyframe gần nhất). Các đoạn được
        đánh số thứ tự rồi phân vào 2 thư mục con: 'Video Chẵn' (số chẵn) và 'Video Lẻ'
        (số lẻ). Nếu `delete_original` bật thì xoá video gốc sau khi cắt xong."""
        if not ext: ext = ".mp4"
        even_dir = os.path.join(folder, "Video Chẵn")
        odd_dir = os.path.join(folder, "Video Lẻ")
        seg_pattern = os.path.join(folder, f"__seg_{clean[:40]}_%04d{ext}")
        cmd = [
            FFMPEG_PATH or "ffmpeg", "-y", "-i", src_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(split_seconds),
            "-reset_timestamps", "1",
            seg_pattern,
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=NO_WINDOW)
        if result.returncode != 0:
            log_error(f"ffmpeg split: {result.stderr[-300:].decode('utf-8', 'ignore')}")
        parts = sorted(glob.glob(os.path.join(folder, f"__seg_{clean[:40]}_*{ext}")))
        if result.returncode != 0 or not parts:
            # Cắt thất bại (ví dụ định dạng không hỗ trợ segment) — dọn rác nếu có và giữ nguyên video gốc
            for p in parts:
                try: os.remove(p)
                except Exception: pass
            return False
        os.makedirs(even_dir, exist_ok=True)
        os.makedirs(odd_dir, exist_ok=True)
        for idx, p in enumerate(parts, start=1):
            target_dir = even_dir if idx % 2 == 0 else odd_dir
            dest = os.path.join(target_dir, f"{clean} - Phần {idx}{ext}")
            c = 1
            while os.path.exists(dest):
                dest = os.path.join(target_dir, f"{clean} - Phần {idx} ({c}){ext}"); c += 1
            try:
                shutil.move(p, dest)
            except Exception:
                pass
        if delete_original:
            try: os.remove(src_path)
            except Exception: pass
        return True

    def _save_script_files(self, tmp_base, folder, clean):
        """Tìm phụ đề tiếng Anh mà yt-dlp vừa tải cho video tạm `tmp_base`, chuyển thành
        1 file .txt kịch bản (lời thoại thuần, đã lược bỏ timestamp/mã dòng) rồi lưu vào
        `folder`. File phụ đề gốc (.srt/.vtt) bị xoá, chỉ giữ lại file .txt.
        Trả về True nếu lấy được script."""
        pattern = os.path.join(self.download_path, f"{tmp_base}.*")
        sub_exts = ('.srt', '.vtt')
        # Ưu tiên .srt (bản đã convert) nếu có, sau đó mới đến .vtt gốc; và ưu tiên đúng
        # thứ tự ngôn ngữ tiếng Anh khai báo trong SCRIPT_LANGS (bản có phụ đề thật > auto-sub)
        candidates = [f for f in glob.glob(pattern) if f.lower().endswith(sub_exts)]
        def _rank(fpath):
            base = os.path.basename(fpath)
            ext_rank = 0 if fpath.lower().endswith('.srt') else 1
            lang_rank = len(SCRIPT_LANGS)
            for idx, lang in enumerate(SCRIPT_LANGS):
                if f".{lang}." in base:
                    lang_rank = idx; break
            return (lang_rank, ext_rank)
        candidates.sort(key=_rank)

        text = ""
        for fpath in candidates:
            text = self._subtitle_to_text(fpath)
            if text:
                break
        # Dọn hết mọi file phụ đề tạm (dùng xong là xoá, không giữ .srt/.vtt gốc)
        for fpath in candidates:
            try: os.remove(fpath)
            except Exception: pass

        if not text:
            return False
        txt_path = os.path.join(folder, f"{clean}_script.txt")
        c = 1
        while os.path.exists(txt_path):
            txt_path = os.path.join(folder, f"{clean}_script ({c}).txt"); c += 1
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            return False
        return True

    @staticmethod
    def _subtitle_to_text(path):
        """Đọc file .srt/.vtt và trả về script dạng văn bản thuần (bỏ số thứ tự,
        timestamp, thẻ định dạng, và các dòng lặp lại liên tiếp của phụ đề tự động)."""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception:
            return ""
        out = []
        for line in raw.splitlines():
            line = line.strip()
            if not line: continue
            if line.upper().startswith("WEBVTT"): continue
            if line.isdigit(): continue
            if '-->' in line: continue
            if line.startswith(("NOTE", "Kind:", "Language:", "STYLE", "::cue")): continue
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            if not clean_line: continue
            if out and out[-1] == clean_line: continue  # bỏ dòng lặp lại liên tiếp (thường gặp ở sub tự động)
            # Sub tự động kiểu cuộn dòng: dòng mới chứa/được chứa trong dòng trước → giữ bản dài hơn
            if out and clean_line in out[-1]: continue
            if out and out[-1] in clean_line:
                out[-1] = clean_line; continue
            out.append(clean_line)
        # Gom thành đoạn (mỗi đoạn ~5 dòng) cho dễ đọc/dùng làm kịch bản
        paras = [" ".join(out[i:i+5]) for i in range(0, len(out), 5)]
        return "\n\n".join(paras)

    # ===== THUMBNAIL =====
    def on_thumb(self):
        url = self.thumb_url.get().strip()
        if not url: messagebox.showerror("Lỗi", "Nhập link!"); return
        self.btn_thumb.configure(state="disabled"); self.thumb_info.configure(text="⏳ Đang tải...")
        threading.Thread(target=self._thumb_work, args=([url],), daemon=True).start()

    def on_thumb_bulk(self):
        txt = self.thumb_bulk.get("1.0", "end").strip()
        urls = [u.strip() for u in txt.split('\n') if u.strip().startswith('http')]
        if not urls: messagebox.showerror("Lỗi", "Dán link!"); return
        self.btn_thumb_bulk.configure(state="disabled")
        threading.Thread(target=self._thumb_work, args=(urls,), daemon=True).start()

    def _thumb_work(self, urls):
        ok = 0
        thumb_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'socket_timeout': 15}
        thumb_opts.update(self._ydl_extra_opts())
        # Reuse single yt-dlp instance for all thumbnails — much faster
        with yt_dlp.YoutubeDL(thumb_opts) as ydl:
            for i, url in enumerate(urls):
                try:
                    self.after(0, lambda idx=i+1: self.thumb_info.configure(text=f"⏳ [{idx}/{len(urls)}]..."))
                    info = ydl.extract_info(url, download=False)
                    title = clean_filename(info.get('title', 'thumb'), info.get('id', 'x'))
                    base = os.path.join(self.download_path, f"{title}_thumb")
                    c = 1
                    while glob.glob(glob.escape(base) + ".*"):
                        base = os.path.join(self.download_path, f"{title}_thumb ({c})"); c += 1
                    if fetch_thumbnail(info, base):
                        ok += 1
                        self.history.append({"url": url, "title": title, "type": "thumbnail", "time": time.strftime("%Y-%m-%d %H:%M")})
                except Exception as e:
                    log_error(f"thumb_work {url}: {e}")
        save_history(self.history)
        self.after(0, lambda: self.thumb_info.configure(text=f"✅ Đã tải {ok}/{len(urls)} thumbnail"))
        self.after(0, lambda: self.btn_thumb.configure(state="normal"))
        self.after(0, lambda: self.btn_thumb_bulk.configure(state="normal"))
        self.after(0, self._refresh_hist)

    # ===== COFFEE FOOTER =====
    def _build_coffee_footer(self):
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, pady=(0, 8), sticky="ew")
        foot.grid_columnconfigure(0, weight=1)
        foot.grid_columnconfigure(1, weight=1)
        foot.grid_columnconfigure(2, weight=1)

        # Dev Info (Bottom Left)
        dev_frame = ctk.CTkFrame(foot, fg_color="transparent")
        dev_frame.grid(row=0, column=0, sticky="sw", padx=16)
        
        dev_lbl = ctk.CTkLabel(dev_frame, text="💻 Dev by VictorChuyen", font=ctk.CTkFont(family=self.FONT, size=12, weight="bold"), text_color="#3498db", cursor="hand2")
        dev_lbl.pack(anchor="w")
        dev_lbl.bind("<Button-1>", lambda e: self._show_about())
        
        dev_sub = ctk.CTkLabel(dev_frame, text="Ủng hộ / Donate", font=ctk.CTkFont(family=self.FONT, size=10), text_color="#7f8c8d", cursor="hand2")
        dev_sub.pack(anchor="w")
        dev_sub.bind("<Button-1>", lambda e: webbrowser.open(DONATE_URL))

    def _show_about(self):
        messagebox.showinfo("Thông Tin Tác Giả & Bản Quyền",
            "⚡ Pro Video Downloader\n\n"
            "💻 Phát triển, Tối ưu & Vận hành: VictorChuyen\n"
            "🤝 Đóng góp nền tảng ban đầu: Hoàng Đức\n\n"
            "🏛 Thư viện nguồn mở cốt lõi:\n"
            "• yt-dlp (Trích xuất media 1000+ nền tảng)\n"
            "• FFmpeg nhúng sẵn (Xử lý & băm video)\n"
            "• CustomTkinter (Giao diện Dark Mode)\n\n"
            "☕ Ủng hộ tác giả: buymeacoffee.com/victorchuyen\n"
            "⚖ Bản quyền thuộc về các tác giả & cộng đồng mã nguồn mở.")

        # Coffee Info (Centered)
        coffee_frame = ctk.CTkFrame(foot, fg_color="transparent")
        coffee_frame.grid(row=0, column=1)

        # Load coffee.png
        coffee_path = os.path.join(os.path.dirname(__file__), "coffee.png")
        try:
            ci = Image.open(coffee_path)
            self._coffee_img = ctk.CTkImage(light_image=ci, dark_image=ci, size=(60, 60))
        except:
            self._coffee_img = None
        # Coffee icon label
        if self._coffee_img:
            self.coffee_lbl = ctk.CTkLabel(coffee_frame, image=self._coffee_img, text="", fg_color="transparent", cursor="hand2")
        else:
            self.coffee_lbl = ctk.CTkLabel(coffee_frame, text="☕", font=ctk.CTkFont(size=36), text_color="#e67e22", cursor="hand2")
        self.coffee_lbl.pack()
        ctk.CTkLabel(coffee_frame, text="Buy Me a Coffee ☕", font=ctk.CTkFont(family=self.FONT, size=10), text_color="#665544").pack()
        self.coffee_lbl.bind("<Button-1>", lambda e: webbrowser.open(DONATE_URL))
        # QR popup
        self._qr_popup = None
        # Load QR once
        self._qr_ctk_img = None
        try:
            qr_path = os.path.join(os.path.dirname(__file__), "real_qr.png")
            if os.path.exists(qr_path):
                qi = Image.open(qr_path)
                self._qr_ctk_img = ctk.CTkImage(light_image=qi, dark_image=qi, size=(200, 200))
        except: pass
        # Bind hover
        self.coffee_lbl.bind("<Enter>", self._show_qr)
        self.coffee_lbl.bind("<Leave>", self._schedule_hide_qr)

    def _show_qr(self, event=None):
        if self._qr_popup and self._qr_popup.winfo_exists():
            return
        if not self._qr_ctk_img:
            return
        p = ctk.CTkToplevel(self)
        p.overrideredirect(True)
        p.attributes('-topmost', True)
        p.configure(fg_color="#0d0906")
        # Build content
        ctk.CTkLabel(p, text="☕ Ủng hộ VictorChuyen", font=ctk.CTkFont(family=self.FONT, size=16, weight="bold"),
            text_color="#f0c070").pack(pady=(12, 6))
        qf = ctk.CTkFrame(p, fg_color="white", corner_radius=10)
        qf.pack(padx=16, pady=6)
        ctk.CTkLabel(qf, image=self._qr_ctk_img, text="", fg_color="white").pack(padx=10, pady=10)
        ctk.CTkLabel(p, text="Quét mã QR hoặc nhấn biểu tượng để donate",
            font=ctk.CTkFont(family=self.FONT, size=11), text_color="#c0946a").pack(pady=(4, 10))
        # Position above coffee icon
        p.update_idletasks()
        pw, ph = p.winfo_reqwidth(), p.winfo_reqheight()
        cx = self.coffee_lbl.winfo_rootx() + self.coffee_lbl.winfo_width() // 2 - pw // 2
        cy = self.coffee_lbl.winfo_rooty() - ph - 8
        p.geometry(f"+{cx}+{cy}")
        self._qr_popup = p
        # Keep popup alive while mouse is on it
        p.bind("<Enter>", lambda e: None)
        p.bind("<Leave>", self._schedule_hide_qr)

    def _schedule_hide_qr(self, event=None):
        self.after(300, self._try_hide_qr)

    def _try_hide_qr(self):
        if not self._qr_popup or not self._qr_popup.winfo_exists():
            return
        try:
            mx, my = self.winfo_pointerx(), self.winfo_pointery()
            cx, cy = self.coffee_lbl.winfo_rootx(), self.coffee_lbl.winfo_rooty()
            cw, ch = self.coffee_lbl.winfo_width(), self.coffee_lbl.winfo_height()
            if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                return
            px, py = self._qr_popup.winfo_rootx(), self._qr_popup.winfo_rooty()
            pw, ph = self._qr_popup.winfo_width(), self._qr_popup.winfo_height()
            if px <= mx <= px + pw and py <= my <= py + ph:
                return
        except: pass
        self._qr_popup.destroy()
        self._qr_popup = None

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()

