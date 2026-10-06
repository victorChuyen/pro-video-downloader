# ⚡ Pro Video Downloader — by VictorChuyen

> Tải video chất lượng cao từ **YouTube, TikTok, Facebook, Instagram, Twitter/X** và **1000+ nền tảng khác** chỉ với 1 click!

---

## 🎬 Video Hướng Dẫn

[![Xem Video Hướng Dẫn](https://img.youtube.com/vi/Bqm_FlEB83A/maxresdefault.jpg)](https://youtu.be/Bqm_FlEB83A)

👉 **[Xem Video Hướng Dẫn trên YouTube](https://youtu.be/Bqm_FlEB83A)**

---

## 📥 Tải Về & Cài Đặt

### Cách 1: Tải file .exe (Khuyến nghị)

1. Vào trang **[Releases](../../releases/latest)**
2. Tải file **`Pro_VideoDownloader_VictorChuyen.exe`**
3. Chạy file — **Không cần cài đặt**, chạy trực tiếp!

> ⚠️ Windows SmartScreen có thể cảnh báo "Unknown Publisher". Click **"More info"** → **"Run anyway"** để chạy.

### Cách 2: Chạy từ Source Code (Dành cho Developer)

```bash
# Clone repo
git clone https://github.com/victorChuyen/pro-video-downloader.git
cd pro-video-downloader

# Cài dependencies
pip install -r requirements.txt

# Chạy app
python app.py
```

---

## ✨ Tính Năng

| Tính năng | Mô tả |
|-----------|--------|
| ▶ **Tải Video** | Dán link → chọn chất lượng → tải ngay |
| ⏬ **Tải Hàng Loạt** | Dán nhiều link cùng lúc, tải tất cả 1 lần |
| 📡 **Quét Kênh** | Quét toàn bộ video của 1 kênh YouTube/TikTok và tải hàng loạt |
| 🖼 **Tải Thumbnail** | Tải ảnh thumbnail chất lượng cao từ video |
| 🕓 **Lịch Sử** | Lưu lại lịch sử tải, dễ quản lý |
| 📁 **Tùy chọn thư mục** | Chọn thư mục lưu file theo ý muốn |

---

## 🎯 Chất Lượng Hỗ Trợ

- 🏆 **Tốt Nhất (Best)** — Tự động chọn chất lượng cao nhất
- 📺 **4K (2160p)** — Ultra HD
- 🖥 **2K (1440p)** — Quad HD
- 💻 **1080p** — Full HD
- 📱 **720p** — HD
- 📱 **480p** — SD
- 🎵 **Chỉ Lấy Nhạc (MP3)** — Trích xuất audio

---

## 🌐 Nền Tảng Hỗ Trợ

YouTube • TikTok • Facebook • Instagram • Twitter/X • Reddit • Vimeo • Dailymotion • Bilibili • Twitch • SoundCloud và **1000+ trang web khác**

---

## 💡 Yêu Cầu Hệ Thống

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4 GB trở lên
- **Kết nối:** Internet ổn định
- **FFmpeg:** Đã được **nhúng sẵn bên trong tool** — chạy được ngay trên mọi máy, không cần tự cài FFmpeg riêng nữa.

> 🍪 **Gặp lỗi "Sign in to confirm you're not a bot"?** Vào phần cuối app, chọn trình duyệt (Chrome/Edge/Firefox/Brave) ở mục "Cookie trình duyệt" — tool sẽ mượn cookie đăng nhập YouTube từ trình duyệt đó để xác nhận không phải bot. Cần đã đăng nhập YouTube trên trình duyệt đó trước, và đóng trình duyệt lại trước khi tải (Chrome/Edge khóa file cookie khi đang mở).

---

## 👥 Nguồn Gốc Dự Án & Tác Giả (Credits & Attribution)

- 💻 **Phát triển, Tối ưu & Vận hành (Lead Developer & Maintainer):** **VictorChuyen**
  - Tối ưu hóa UI/UX Modern Dark Mode với CustomTkinter.
  - Tích hợp động cơ bóc tách kịch bản sạch (.txt) phục vụ AI Workflow.
  - Xây dựng module tự động cắt video đa đoạn (Chẵn/Lẻ) bằng FFmpeg nhúng.
  - Tích hợp trích xuất Metadata JSON phân tích đối thủ & cơ chế vượt bot-check cookie.
- 🤝 **Đóng góp nền tảng ban đầu (Original Contributor):** **Hoàng Đức** (`hoangvant77internet-sudo`)
- ☕ **Ủng hộ tác giả / Donate:** [buymeacoffee.com/victorchuyen](https://buymeacoffee.com/victorchuyen)

### 🏛️ Thư Viện Nền Tảng (Open Source Core):
- **yt-dlp**: Trình trích xuất video đa nền tảng mã nguồn mở mạnh mẽ nhất thế giới.
- **CustomTkinter**: Thư viện giao diện người dùng hiện đại phát triển bởi *Tom Schimansky*.
- **FFmpeg & imageio-ffmpeg**: Động cơ xử lý và băm nhỏ video đa luồng bởi *Fabrice Bellard* & FFmpeg Team.
- **Pillow (PIL)**: Thư viện xử lý hình ảnh thumbnail chuyên nghiệp.

> ⚖️ **Tuyên bố miễn trừ trách nhiệm (Disclaimer):**  
> Công cụ này được phát triển phục vụ mục đích học tập, nghiên cứu công nghệ, sao lưu tư liệu cá nhân và hỗ trợ người sáng tạo nội dung phân tích thị trường hợp pháp (Fair Use). Người sử dụng tự chịu trách nhiệm về bản quyền và tuân thủ điều khoản dịch vụ của các nền tảng khi khai thác nội dung.

---

## 📋 Changelog

### v1.0.0 (2026-04-29)
- 🎉 Phiên bản đầu tiên
- ▶ Tải video đơn lẻ từ 1000+ nền tảng
- ⏬ Tải hàng loạt nhiều link cùng lúc
- 📡 Quét & tải toàn bộ kênh YouTube/TikTok
- 🖼 Tải thumbnail chất lượng cao
- 🕓 Lịch sử tải video
- 📁 Tùy chọn thư mục lưu

---

⭐ **Nếu thấy hữu ích, hãy Star repo này để ủng hộ!** ⭐
