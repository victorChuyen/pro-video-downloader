# ⚡ HƯỚNG DẪN SỬ DỤNG NHANH — PRO VIDEO DOWNLOADER
> **Dành cho:** Content Creator, Kênh YouTube Reup/Review, Kênh TikTok Shorts, Marketer & Dân MMO làm nội dung đa nền tảng.

---

## 👥 NGUỒN GỐC DỰ ÁN & BẢN QUYỀN TÁC GIẢ (CREDITS & ATTRIBUTION)

- 💻 **Phát triển, Tối ưu & Vận hành (Lead Developer & Maintainer):** **VictorChuyen**
  - Trực tiếp nâng cấp và tối ưu toàn diện UI/UX Modern Dark Mode với CustomTkinter.
  - Tích hợp động cơ bóc tách kịch bản sạch (`.txt`) gộp đoạn thông minh phục vụ quy trình làm việc với AI (ChatGPT / Gemini / ElevenLabs).
  - Kiến trúc hóa module tự động băm nhỏ video đa đoạn (phân chia tự động thư mục Video Chẵn / Video Lẻ) bằng FFmpeg nhúng sẵn.
  - Bổ sung module xuất trích xuất Metadata JSON phục vụ phân tích đối thủ, gián điệp thẻ tags và tối ưu hóa SEO YouTube.
  - Xử lý triệt để cơ chế vượt rào Bot-Check bằng file Cookies & Session Browser, tính năng Auto-Update yt-dlp 1-click.
- 🤝 **Đóng góp nền tảng ban đầu (Original Contributor):** **Hoàng Đức** (`hoangvant77internet-sudo`).
- ☕ **Ủng hộ tác giả / Donate:** [buymeacoffee.com/victorchuyen](https://buymeacoffee.com/victorchuyen)

### 🏛️ Thư Viện Nền Tảng Mã Nguồn Mở (Open Source Core):
- **yt-dlp**: Trình trích xuất media đa nền tảng mạnh mẽ nhất thế giới (Unlicense).
- **CustomTkinter**: Thư viện giao diện đồ họa hiện đại phát triển bởi *Tom Schimansky* (MIT License).
- **FFmpeg & imageio-ffmpeg**: Động cơ xử lý và băm nhỏ video đa luồng bởi *Fabrice Bellard* & FFmpeg Team (LGPL/GPL).
- **Pillow (PIL)**: Thư viện xử lý hình ảnh thumbnail chất lượng cao (HPND License).

> ⚖️ **Tuyên bố trách nhiệm & Bản quyền (Disclaimer & Fair Use):**  
> Công cụ này được phát triển vì mục đích học tập, nghiên cứu công nghệ, sao lưu tư liệu cá nhân và hỗ trợ người sáng tạo nội dung phân tích thị trường hợp pháp (Fair Use). Người sử dụng tự chịu trách nhiệm về bản quyền và tuân thủ điều khoản dịch vụ của các nền tảng khi khai thác nội dung.

---

## 🎯 1. TOOL NÀY DÙNG ĐỂ LÀM GÌ?
Đây không chỉ là tool tải video thông thường, mà là **Cỗ máy khai thác & đóng gói nguyên liệu Content tự động** từ 1000+ nền tảng (YouTube, TikTok, Facebook, Instagram, Douyin, Bilibili...):
1. **Bóc tách kịch bản gốc (Script)**: Tự trích xuất phụ đề, lọc bỏ rác cuộn dòng, gom thành đoạn văn bản mượt mà (`.txt`) để bạn ném vào ChatGPT/Gemini viết lại hoặc dịch sang tiếng Việt.
2. **Tự động băm nhỏ video dài thành Shorts/Reels**: Chỉ cần nhập số giây (ví dụ: `60`), tool tự dùng FFmpeg cắt thành các tập ngắn (Phần 1, 2, 3...) và tự chia vào 2 thư mục `Video Chẵn` / `Video Lẻ` để đăng so le đa kênh.
3. **Hút trọn bộ tư liệu SEO đối thủ**: Lấy ảnh Thumbnail HD/4K + File Metadata JSON (Tiêu đề, mô tả, bộ thẻ tags, lượt view, thời lượng) phục vụ nghiên cứu ngách.
4. **Quét sạch toàn bộ Kênh / Playlist**: Nhập link kênh YouTube bất kỳ, tool tự gom 10, 20 hay 100 video mới nhất về máy chỉ bằng 1 nút bấm.

---

## 📁 2. KẾT QUẢ ĐẦU RA TRONG THƯ MỤC CỦA BẠN LÀ GÌ?
Mỗi khi tải 1 video, tool tự động gom tất cả vào **1 thư mục riêng biệt mang tên video đó**:

```text
📁 Downloads/VideoDownloader/Ten_Video/
 ├── 🎬 Ten_Video.mp4              (Video gốc chất lượng cao nhất lên tới 4K)
 ├── 🖼 Ten_Video_thumb.jpg        (Ảnh Thumbnail gốc nét căng)
 ├── 📝 Ten_Video_script.txt       (Kịch bản lời thoại sạch, dùng ngay cho AI)
 ├── 📊 Ten_Video_metadata.json    (Thẻ Tags, Views, Lời mô tả gốc để làm SEO)
 ├── 📂 Video Lẻ/                  (Các đoạn cắt Phần 1, 3, 5... mỗi đoạn 60s)
 └── 📂 Video Chẵn/                (Các đoạn cắt Phần 2, 4, 6... mỗi đoạn 60s)
```

---

## 🚀 3. HƯỚNG DẪN DÙNG TRONG 3 BƯỚC (CHƯA ĐẦY 30 GIÂY)

### 🔹 Cách 1: Tải 1 Video Đầy Đủ "Combo Tư Liệu"
1. **Bước 1**: Mở app (Click đúp file `run.bat`).
2. **Bước 2**: Dán link video vào ô URL (Bấm nút **📋** để dán nhanh từ clipboard).
3. **Bước 3**: 
   - Chọn chất lượng (Khuyên dùng: **1080p** hoặc **Tốt Nhất**).
   - Tích chọn **📝 Kèm Script tiếng Anh** (nếu muốn lấy kịch bản thoại).
   - Tích chọn **✂️ Cắt video** và gõ `60` (nếu muốn băm nhỏ làm TikTok/Shorts).
4. Bấm **▶ BẮT ĐẦU TẢI** ➔ Bấm **📂 MỞ THƯ MỤC** để nhận thành phẩm!

---

### 🔹 Cách 2: Tải Hàng Loạt (Bulk Download)
- Chuyển sang tab **⏬ Hàng Loạt**.
- Dán danh sách link (mỗi dòng 1 link).
- Bấm **⏬ TẢI TẤT CẢ** ➔ App sẽ tải lần lượt từng video kèm đầy đủ thumbnail & script. *Nếu link nào đã tải trước đó, app tự động nhận diện và bỏ qua để tránh trùng lặp.*

---

### 🔹 Cách 3: Quét & Hút Cả Kênh Đối Thủ (Channel Scan)
1. Chuyển sang tab **📡 Quét Kênh**.
2. Dán link kênh (Ví dụ: `https://www.youtube.com/@MrBeast`).
3. Chọn số lượng cần lấy ở mục **Giới hạn** (10, 20, 50 hoặc Tất cả).
4. Bấm **🔍 QUÉT KÊNH** ➔ App liệt kê danh sách video mới.
5. Bấm **⏬ TẢI TẤT CẢ** ➔ Toàn bộ video của kênh sẽ được kéo về máy.

---

### 🔹 Cách 4: Tách Thumbnail Nhanh Để Làm Đồ Họa
- Chuyển sang tab **🖼 Thumbnail**.
- Dán 1 link hoặc 1 danh sách nhiều link.
- Bấm **TẢI THUMBNAIL** ➔ Thu về toàn bộ ảnh bìa sắc nét để làm mẫu thiết kế.

---

## 💡 4 CÔNG THỨC THỰC CHIẾN ĐỂ KIẾM TIỀN & XÂY KÊNH YOUTUBE HIỆU QUẢ

| Mô hình làm Content | Cách tool hỗ trợ bạn | Kết quả đạt được |
| :--- | :--- | :--- |
| **1. Kênh Review / Tin tức / Kể chuyện dịch thuật** | Tải video chọn kèm **📝 Script** ➔ Copy nội dung file `_script.txt` ném vào ChatGPT với prompt: *"Dịch và viết lại kịch bản này sang văn phong kịch tính tiếng Việt"* ➔ Đưa vào ElevenLabs/CapCut đọc voice. | Xong kịch bản và ý tưởng trong **2 phút** thay vì ngồi gõ chay nghe lại từng câu mất 1 tiếng. |
| **2. Bán Content / Kênh Reup Podcast cắt ngắn** | Chọn **✂️ Cắt video 60s** ➔ Tool tự chia tập `Phần 1, Phần 2, Phần 3...` vào 2 folder Chẵn/Lẻ. | 1 Podcast dài 1 tiếng cắt được **60 video ngắn** sẵn sàng nuôi 2 kênh TikTok/Reels chạy song song. |
| **3. Nghiên cứu & Gián điệp từ khóa đối thủ** | Mở file `_metadata.json` của video nhiều triệu view xem họ gắn những `tags` nào, đặt `title` và `description` ra sao. | Tối ưu SEO cho video của mình ăn đề xuất theo đúng thuật toán YouTube. |
| **4. Kho B-Roll / Footage dựng phim miễn phí** | Quét các kênh chuyên phong cảnh, khoa học, review công nghệ tải về lưu trữ. | Sở hữu kho video minh họa chất lượng cao không lo thiếu cảnh khi biên tập. |

---

## 🛠️ LƯU Ý KHI GẶP LỖI THƯỜNG GẶP
- **YouTube bắt xác minh Bot ("Sign in to confirm you're not a bot")**: 
  - *Cách 1*: Ở chân trang app, click **📁 Chọn cookies.txt** và chọn file cookies xuất từ trình duyệt (dùng extension *Get cookies.txt LOCALLY*).
  - *Cách 2*: Chọn trình duyệt **Firefox** ở mục Cookie.
- **Cập nhật thuật toán tải**: YouTube thường xuyên đổi mã nguồn, nếu gặp lỗi không tải được, chỉ cần bấm nút **⟳ Cập nhật yt-dlp** ở góc dưới cùng của app để tự động nâng cấp lõi mới nhất.
