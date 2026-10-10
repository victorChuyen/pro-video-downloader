import urllib.request
import json
import time

url = "http://127.0.0.1:8001/api/tts"
sample = "Đầu tiên là phụ nữ mang thai hoặc đang cho con bú. Với nhiều loại thảo dược, dữ liệu an toàn cho hai đối tượng này vẫn còn rất hạn chế. Có những chất có thể đi qua nhau thai, ảnh hưởng đến sự phát triển của thai nhi, hoặc tiết qua sữa mẹ và tác động đến hệ tiêu hóa, chuyển hóa của trẻ sơ sinh. Người đang mắc các bệnh lý mạn tính như tiểu đường, tim mạch, huyết áp hoặc đang sử dụng thuốc điều trị cũng cần hết sức thận trọng. Các thành phần trong thảo mộc có thể tương tác với thuốc tây, làm giảm hiệu quả điều trị hoặc nguy hiểm hơn là làm tăng độc tính của thuốc. "

# Generate ~8.700 characters
text = sample * 15
print(f"Generated text length: {len(text)} characters")

data = json.dumps({
    "text": text,
    "voice": "Nam Triệu Mẹo - Đừng Chủ Qu · 😌 Trầm ấm",
    "temperature": 0.8,
    "top_k": 25
}).encode("utf-8")

req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

start = time.time()
print("Sending request to /api/tts...")
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        content = resp.read()
        elapsed = time.time() - start
        print(f"SUCCESS in {elapsed:.2f}s! Received {len(content)} bytes of WAV audio")
except urllib.error.HTTPError as e:
    err = e.read().decode("utf-8", errors="replace")
    print(f"HTTP ERROR {e.code}: {err}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
