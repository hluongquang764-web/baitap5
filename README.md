# BÀI TẬP LỚN 5 — PHÁT TRIỂN ỨNG DỤNG VỚI MÃ NGUỒN MỞ (TEE0421)

**Họ và tên:** Lương Quang Hà  
**MSSV:** K225480106010  
**Lớp:** 58KTPM / K58KTP.K01  
**Môn:** Phát triển ứng dụng với mã nguồn mở — TEE0421  

---

## A. LÝ THUYẾT

---

### 1. Docker là gì?

**Docker** là nền tảng mã nguồn mở (open-source) cho phép đóng gói ứng dụng cùng toàn bộ dependencies (thư viện, runtime, cấu hình, biến môi trường) vào một đơn vị tiêu chuẩn gọi là **container**.

#### Các khái niệm cốt lõi

| Khái niệm | Giải thích |
|---|---|
| **Image** | Bản thiết kế (blueprint) chỉ đọc để tạo container. Được build từ `Dockerfile`. |
| **Container** | Một instance đang chạy của image. Nhẹ, cô lập, có thể start/stop/remove. |
| **Dockerfile** | File văn bản chứa tập lệnh để build image (FROM, RUN, COPY, CMD…). |
| **Docker Hub** | Registry công cộng lưu trữ và chia sẻ image (giống GitHub nhưng cho image). |
| **Docker Engine** | Daemon chạy nền trên host, quản lý container, image, network, volume. |

#### Docker khác VM như thế nào?

```
┌─────────────────────────────┐    ┌─────────────────────────────┐
│         DOCKER              │    │       VIRTUAL MACHINE       │
├──────────┬──────────────────┤    ├──────────┬──────────────────┤
│  App A   │  App B           │    │  App A   │  App B           │
├──────────┴──────────────────┤    ├──────────┴──────────────────┤
│     Docker Engine           │    │  Guest OS│  Guest OS        │
├─────────────────────────────┤    ├──────────┴──────────────────┤
│      Host OS (Kernel)       │    │       Hypervisor            │
├─────────────────────────────┤    ├─────────────────────────────┤
│         Hardware            │    │         Hardware            │
└─────────────────────────────┘    └─────────────────────────────┘
  Dùng chung kernel → nhẹ hơn         Mỗi VM có OS riêng → nặng hơn
```

---

### 2. Các keyword trong `docker-compose.yml`

`docker-compose.yml` là file cấu hình định nghĩa và chạy nhiều container cùng lúc bằng một lệnh duy nhất.

#### 2.1 Cấu trúc tổng quan

```yaml
version: '3.9'

services:       # Danh sách các container
  ten_service:
    ...

networks:       # Định nghĩa mạng nội bộ
  ...

volumes:        # Định nghĩa volume lưu dữ liệu
  ...
```

---

#### 2.2 Các keyword mô tả một `service`

| Keyword | Ý nghĩa | Ví dụ minh hoạ |
|---|---|---|
| `image` | Chỉ định Docker image để tạo container | `image: mariadb:11` |
| `build` | Build image từ Dockerfile thay vì dùng image có sẵn | `build: ./flask-api` |
| `container_name` | Đặt tên cố định cho container (thay vì tên ngẫu nhiên) | `container_name: bt5_nodered` |
| `ports` | Ánh xạ cổng `HOST:CONTAINER` — truy cập từ bên ngoài | `ports: - "1880:1880"` |
| `expose` | Mở cổng nội bộ giữa các container (không ra host) | `expose: - "5000"` |
| `environment` | Truyền biến môi trường vào container | `environment: MYSQL_ROOT_PASSWORD: root123` |
| `env_file` | Đọc biến môi trường từ file `.env` | `env_file: - .env` |
| `volumes` | Mount thư mục host hoặc named volume vào container | `volumes: - ./html:/usr/share/nginx/html` |
| `networks` | Gắn service vào một hoặc nhiều network | `networks: - bt5_net` |
| `depends_on` | Đảm bảo service khác khởi động trước service này | `depends_on: - mariadb` |
| `restart` | Chính sách tự khởi động lại khi container dừng | `restart: unless-stopped` |
| `command` | Ghi đè lệnh CMD mặc định của image | `command: ["python", "app.py"]` |
| `healthcheck` | Định kỳ kiểm tra container có đang hoạt động đúng không | `healthcheck: test: ["CMD", "curl", "-f", "http://localhost"]` |
| `hostname` | Đặt hostname cho container trong network nội bộ | `hostname: grafana` |
| `user` | Chạy container bằng user cụ thể (bảo mật) | `user: "1000:1000"` |
| `privileged` | Cấp quyền đầy đủ host cho container (dùng thận trọng) | `privileged: false` |
| `stdin_open` | Giữ stdin mở (tương đương `-i` trong `docker run`) | `stdin_open: true` |
| `tty` | Cấp pseudo-TTY (tương đương `-t`) | `tty: true` |

---

#### 2.3 Các keyword mô tả `network`

```yaml
networks:
  bt5_net:
    driver: bridge      # bridge (mặc định), host, overlay, none
    name: bt5_network   # Tên tuỳ chỉnh (không theo quy tắc đặt tên Compose)
```

| Keyword | Ý nghĩa |
|---|---|
| `driver: bridge` | Network ảo nội bộ, các container giao tiếp qua tên service |
| `driver: host` | Container dùng trực tiếp network của host |
| `driver: overlay` | Dùng cho Docker Swarm — kết nối nhiều host |
| `external: true` | Sử dụng network đã tạo sẵn bên ngoài Compose |

---

#### 2.4 Các keyword mô tả `volume`

```yaml
volumes:
  influxdb_data:        # Named volume — Docker quản lý, tồn tại độc lập
    driver: local
  mariadb_data:
```

| Loại volume | Cú pháp | Ý nghĩa |
|---|---|---|
| **Bind mount** | `./host_dir:/container_dir` | Mount thư mục cụ thể từ host |
| **Named volume** | `volume_name:/container_dir` | Docker tự quản lý, dữ liệu không mất khi container bị xóa |
| **Anonymous** | `/container_dir` | Volume tạm, mất khi container xóa |

---

#### 2.5 Ví dụ `docker-compose.yml` minh hoạ đầy đủ

```yaml
version: '3.9'

services:
  mariadb:
    image: mariadb:11
    container_name: bt5_mariadb
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: monitor_db
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - bt5_net

  nodered:
    image: nodered/node-red:latest
    container_name: bt5_nodered
    restart: unless-stopped
    ports:
      - "1880:1880"
    volumes:
      - nodered_data:/data
    depends_on:
      - mariadb
      - influxdb
    networks:
      - bt5_net

  influxdb:
    image: influxdb:2.7
    container_name: bt5_influxdb
    restart: unless-stopped
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2
    networks:
      - bt5_net

  grafana:
    image: grafana/grafana:latest
    container_name: bt5_grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - influxdb
    networks:
      - bt5_net

  flask_api:
    build: ./flask-api
    container_name: bt5_flask
    restart: unless-stopped
    expose:
      - "5000"
    depends_on:
      - mariadb
    networks:
      - bt5_net

  nginx:
    image: nginx:alpine
    container_name: bt5_nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - flask_api
      - grafana
    networks:
      - bt5_net

networks:
  bt5_net:
    driver: bridge

volumes:
  mariadb_data:
  influxdb_data:
  nodered_data:
```

---

### 3. Ưu điểm khi triển khai ứng dụng sử dụng Docker

| # | Ưu điểm | Giải thích |
|---|---|---|
| 1 | **Nhất quán môi trường** | Container chạy giống hệt nhau trên mọi máy (dev/test/production). Loại bỏ hoàn toàn lỗi "works on my machine". |
| 2 | **Cô lập service** | Mỗi service (MariaDB, Grafana, Node-RED…) chạy trong container riêng, không xung đột port hay thư viện với nhau. |
| 3 | **Triển khai nhanh** | Chỉ cần `docker compose up -d` là toàn bộ hệ thống sẵn sàng trong vài giây. |
| 4 | **Dễ mở rộng (scale)** | Tăng số replica của một service chỉ bằng một tham số. |
| 5 | **Quản lý dependency đơn giản** | Không cần cài thủ công từng phần mềm lên host OS; mọi thứ đã có trong image. |
| 6 | **Dễ backup và khôi phục** | Export image thành file `.tar`, copy sang máy khác, load lại là xong. |
| 7 | **Tái sử dụng** | Image đã build có thể push lên Docker Hub và dùng lại ở bất kỳ đâu. |
| 8 | **Phù hợp CI/CD** | Tích hợp tốt với GitHub Actions, Jenkins — build, test, deploy đều tự động. |

---

### 4. Triển khai ứng dụng Docker lên máy chủ không có Internet

> **Tình huống:** App đã chạy OK trên laptop cá nhân (có internet). Giờ cần triển khai lên máy chủ thật **không kết nối internet**.

#### Các bước thực hiện

**Bước 1 — Trên máy DEV (có internet): Đảm bảo tất cả image đã được pull về local**

```bash
docker compose pull
```

**Bước 2 — Export toàn bộ image thành file nén**

```bash
# Lấy danh sách tất cả image trong compose file rồi save
docker save $(docker compose config --images | tr '\n' ' ') \
  -o bt5_images.tar

# Nén lại để giảm dung lượng
gzip bt5_images.tar
# → Tạo ra file: bt5_images.tar.gz
```

**Bước 3 — Copy sang máy chủ qua USB / SCP / mạng LAN nội bộ**

```bash
# Qua SCP (nếu cùng mạng LAN)
scp bt5_images.tar.gz user@192.168.1.100:/opt/bt5/

# Copy thêm source code và file cấu hình
scp -r ./bt5_project user@192.168.1.100:/opt/bt5/
```

**Bước 4 — Trên máy chủ: Load lại các image từ file nén**

```bash
cd /opt/bt5
gunzip bt5_images.tar.gz
docker load -i bt5_images.tar
```

> Sau lệnh này, `docker images` sẽ hiển thị đầy đủ các image đã được nạp vào.

**Bước 5 — Khởi động hệ thống**

```bash
cd /opt/bt5/bt5_project
docker compose up -d
```

**Bước 6 — Kiểm tra**

```bash
docker compose ps          # Xem trạng thái các container
docker compose logs -f     # Xem log realtime
```

#### Tóm tắt quy trình

```
[Máy DEV - có internet]          [Máy chủ - không internet]
        │                                    │
  docker compose pull              docker load -i bt5_images.tar
        │                                    │
  docker save → bt5_images.tar.gz  →  copy  │
        │                                    │
  copy source code + compose.yml   →  copy  │
                                             │
                                   docker compose up -d
                                             │
                                        ✅ Hệ thống chạy
```

---

# B. THỰC HÀNH — APP MONITOR + ALERT GIÁ XĂNG DẦU REALTIME

---

## Kiến trúc hệ thống

```
[Dữ liệu giá xăng]
        │ HTTP GET (mỗi 5 phút)
        ▼
  [Node-RED] ──────────────────────────────────────► [Telegram Bot Alert]
        │                                              (khi vượt ngưỡng)
        ├──► [MariaDB]  ◄── [Flask API] ◄── [Nginx] ◄── [Cloudflare Tunnel]
        │    (tức thời)                        ▲                ▲
        │                                      │           Browser
        └──► [InfluxDB] ──► [Grafana] ─────────┘
             (lịch sử)    (biểu đồ iframe)
```

**Ngưỡng cảnh báo giá xăng (VNĐ/lít):**

| Loại | ALERT LOW | OK | ALERT HIGH |
|---|---|---|---|
| RON95-III | < 20,000 | 20,000 – 25,000 | > 25,000 |
| RON92-II | < 19,000 | 19,000 – 24,000 | > 24,000 |
| DO 0.05S | < 18,000 | 18,000 – 23,000 | > 23,000 |

---

## Cấu trúc thư mục dự án

```
bt5/
├── docker-compose.yml          ← Định nghĩa 7 service Docker
├── nginx/
│   └── nginx.conf              ← Cấu hình webserver + proxy
├── frontend/
│   └── index.html              ← Giao diện HTML/JS/CSS realtime
├── flask-api/
│   ├── Dockerfile              ← Build image Flask
│   ├── requirements.txt        ← Thư viện Python
│   └── app.py                  ← API trả JSON giá tức thời
├── mariadb/
│   └── init/
│       └── 01_init.sql         ← Tạo bảng petrol_price tự động
└── nodered/
    └── flows.json              ← Node-RED flow (import thủ công)
```

---

## Các service trong docker-compose.yml

| Service | Image | Vai trò |
|---|---|---|
| bt5-mariadb | mariadb:latest | Lưu giá xăng tức thời |
| bt5-influxdb | influxdb:2.7 | Lưu lịch sử (time-series) |
| bt5-nodered | nodered/node-red:latest | Lấy data, xử lý, alert |
| bt5-grafana | grafana/grafana:latest | Vẽ biểu đồ lịch sử |
| bt5-flask | (build local) | API trả JSON từ MariaDB |
| bt5-nginx | nginx:alpine | Webserver + proxy |
| bt5-cloudflare | cloudflare/cloudflared:latest | Tunnel ra internet |

---

## Quá trình thực hiện

### Bước 1 — Chuẩn bị máy chủ

SSH vào máy chủ Ubuntu:

```bash
ssh luongha@172.30.122.88
```

Kiểm tra dung lượng disk:

```bash
df -h /
```

<img width="1174" height="613" alt="image" src="https://github.com/user-attachments/assets/20b1d9a9-17ec-4a58-9f1c-452c38bcbcc8" />

Dọn dẹp disk (nếu cần):

```bash
docker rmi n8nio/n8n:latest phpmyadmin:latest wordpress:latest
df -h /
```

---

### Bước 2 — Tạo cấu trúc thư mục

```bash
cd ~
mkdir bt5
cd bt5
mkdir frontend flask-api nginx mariadb nodered
mkdir mariadb/init
sudo chown -R 1000:1000 ./nodered
ls -la
```

<img width="1287" height="758" alt="image" src="https://github.com/user-attachments/assets/321a4de9-b9fc-43bf-8938-8edf0e804f28" />


---

### Bước 3 — Tạo các file cấu hình

Tạo lần lượt các file bằng lệnh `cat > file << 'EOF'`:

```bash
# Tạo docker-compose.yml
cat > docker-compose.yml << 'EOF'
... (nội dung file)
EOF

# Tạo SQL init
cat > mariadb/init/01_init.sql << 'EOF'
... (nội dung file)
EOF

# Tạo Flask API
cat > flask-api/requirements.txt << 'EOF'
... (nội dung file)
EOF

cat > flask-api/Dockerfile << 'EOF'
... (nội dung file)
EOF

cat > flask-api/app.py << 'EOF'
... (nội dung file)
EOF

# Tạo nginx config
cat > nginx/nginx.conf << 'EOF'
... (nội dung file)
EOF

# Tạo frontend
cat > frontend/index.html << 'EOF'
... (nội dung file)
EOF
```

Kiểm tra tất cả file đã tạo:

```bash
find . -type f | sort
```

<img width="1179" height="689" alt="image" src="https://github.com/user-attachments/assets/13a2dbb6-8a4b-4a28-9fd5-f5d37473cced" />
<img width="1429" height="834" alt="image" src="https://github.com/user-attachments/assets/94c9c786-2c36-4d3c-98a3-135db4b4e05c" />

---

### Bước 4 — Cấu hình Cloudflare Tunnel

1. Vào https://one.dash.cloudflare.com → **Networks → Tunnels → Create a tunnel**
2. Đặt tên tunnel: `bt5-tunnel` → **Save**
3. Chọn tab **Docker** → copy token (`eyJ...`)
4. Thêm Public Hostname:
   - Subdomain: `k58-bt5`
   - Domain: `luongquangha.io.vn`
   - Service: `http://bt5-nginx:80`
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/37765fc5-350a-4809-ad00-1ac696fcee57" />


Điền token vào `docker-compose.yml`:

```bash
nano docker-compose.yml
# Tìm dòng: command: tunnel --no-autoupdate run --token PASTE_YOUR_TOKEN_HERE
# Thay bằng token thật
```

---

### Bước 5 — Khởi động hệ thống

```bash
docker-compose up -d
```
<img width="1246" height="786" alt="image" src="https://github.com/user-attachments/assets/797bf5f7-55a9-4ec6-9e39-1fe8403e363d" />



Kiểm tra trạng thái các container:

```bash
docker-compose ps
```

<img width="1318" height="862" alt="image" src="https://github.com/user-attachments/assets/e1a99b2e-73c6-442c-9002-bedb741e4e25" />


```
     Name                   Command                  State        Ports
-------------------------------------------------------------------------
bt5-cloudflare   cloudflared --no-autoupdat ...   Up
bt5-flask        python app.py                    Up             5000/tcp
bt5-grafana      /run.sh                          Up             3000/tcp
bt5-influxdb     /entrypoint.sh influxd           Up             8086/tcp
bt5-mariadb      docker-entrypoint.sh mariadbd    Up             3306/tcp
bt5-nginx        /docker-entrypoint.sh ngin ...   Up             80/tcp
bt5-nodered      ./entrypoint.sh                  Up (healthy)   1880/tcp
```

---

### Bước 6 — Cài palette và cấu hình Node-RED

Truy cập Node-RED: https://k58-bt5.luongquangha.io.vn/nodered/

**Cài palette:**

Menu ☰ → **Manage palette** → tab **Install** → tìm và cài:
- `node-red-node-mysql` (kết nối MariaDB)
- `node-red-contrib-telegrambot` (gửi Telegram alert)

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/606eeb18-7964-48de-8573-c2dbaa42b501" />



**Import flow:**

Menu ☰ → **Import** → paste nội dung file `nodered/flows.json` → **Import**

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f9e50b6f-3f8c-492f-8a15-c624f16283b0" />


**Cấu hình node Lưu MariaDB:**

Double-click node **Set SQL query** → kiểm tra code SQL.  
Double-click node **Lưu MariaDB** → click ✏️ → điền:
- Host: `bt5-mariadb`
- Port: `3306`
- Database: `petrol_db`
- User: `petrol_user`
- Password: `petrol123`

**Cấu hình node Gửi Telegram:**

Double-click node **Gửi Telegram** → click ✏️ → điền:
- Bot Name: `BT5PetrolMonitorBot`
- Token: `8910946918:AAFlJ9lAUFbuU_lh5RDKazVRHzy9WNhR_wQ`

Click **Deploy** → thấy thông báo **Successfully deployed**.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5d3a33f2-0c4d-49c3-853e-a454b79cc9bc" />

---

### Bước 7 — Kiểm tra dữ liệu trong Node-RED Debug

Click nút **inject** (ô vuông trái node "Mỗi 5 phút") để chạy thủ công.

Mở tab **Debug messages** → xem kết quả:

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2abb4c6f-4b5a-45ff-8b8d-b8609deba539" />


---

### Bước 8 — Kiểm tra website realtime

Truy cập: https://k58-bt5.luongquangha.io.vn

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/06a2844c-a305-43be-aa73-36a487f48143" />


**Giải thích hoạt động:**
- JavaScript gọi `fetch('/api/petrol')` mỗi 10 giây
- Flask API truy vấn MariaDB → trả JSON
- Frontend cập nhật giao diện tự động, không cần F5

---

### Bước 9 — Cấu hình Grafana

Truy cập: https://k58-bt5.luongquangha.io.vn/grafana/

Đăng nhập: `admin` / `admin123`

**Thêm datasource InfluxDB:**

**Connections → Data sources → Add data source → InfluxDB**

Điền:
- Query language: **Flux**
- URL: `http://bt5-influxdb:8086`
- Organization: `tnut`
- Token: `my-super-secret-token-bt5`
- Default Bucket: `petrol_history`

Click **Save & test** → thấy **"datasource is working. 3 buckets found"**

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7f350e71-318d-47be-b4b4-cb93213a1136" />

**Tạo dashboard:**

Click **building a dashboard from scratch** → **Add panel** → **Configure visualization**

Chọn Data source: **influxdb**

Paste query Flux:

```flux
from(bucket: "petrol_history")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "petrol_price")
  |> filter(fn: (r) => r._field == "price")
```

Click **Refresh** → thấy biểu đồ 3 đường.

Đặt Title panel: `BT5 - Monitor Gia Xang` → **Save** → đặt tên dashboard: `BT5 - Monitor Gia Xang` → **Save**.

_<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a6bbb0f9-94ca-48b6-a91e-a9e139405253" />


---

### Bước 10 — Nhúng Grafana vào frontend (iframe)

Click vào panel → **⋮ (3 chấm)** → **Share** → **Embed** → copy URL trong thẻ `<iframe src="...">`

Cập nhật `frontend/index.html` — thay URL iframe:

```bash
# Sửa dòng src trong thẻ iframe thành:
# /grafana/d-solo/DASHBOARD_UID/new-dashboard?orgId=1&panelId=1&refresh=30s
```

Reload nginx:

```bash
docker-compose restart bt5-nginx
```

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1ddc66e4-e5dd-40ff-aacf-303384fd969d" />


---

### Bước 11 — Test Telegram Alert

**Tạo bot Telegram:**
1. Mở Telegram → tìm `@BotFather` → `/newbot`
2. Đặt tên: `BT5PetrolMonitorBot`
3. Username: `BT5PetrolMonitor_bot`
4. Copy token: `8910946918:AAFlJ9lAUFbuU_lh5RDKazVRHzy9WNhR_wQ`

**Lấy Chat ID nhóm:**
1. Tạo nhóm Telegram → add `@BT5PetrolMonitor_bot` vào nhóm
2. Gửi tin nhắn `hello` trong nhóm
3. Truy cập: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Tìm `chat.id` trong JSON → đây là Chat ID (số âm)

> Chat ID nhóm: `-5251862594`

**Test alert:**

Double-click node **Parse giá xăng** trong Node-RED → đổi giá RON95 thành `19000` (dưới ngưỡng 20,000) → **Done** → **Deploy** → click nút inject thủ công.


> ```
> ⛽ CẢNH BÁO GIÁ XĂNG DẦU
> 🔵 RON95-III: 19,000 đ — DƯỚI NGƯỠNG THẤP (< 20,000)
> ⏰ 05:46:21 7/6/2026
> ```
<img width="1290" height="2796" alt="image" src="https://github.com/user-attachments/assets/231856c2-61d2-4469-b889-8c0e44697586" />


---

### Bước 12 — Xuất, xóa và khôi phục container

**Xuất image ra file nén:**

```bash
cd ~/bt5
docker save bt5_bt5-flask:latest -o bt5_flask.tar
ls -lh bt5_flask.tar
```

<img width="1456" height="819" alt="image" src="https://github.com/user-attachments/assets/3206145b-dd48-448b-b2df-5a94d3f292bb" />

**Xóa toàn bộ container:**

```bash
docker stop bt5-grafana
docker rm bt5-grafana
docker-compose down
docker ps -a
```
<img width="1456" height="819" alt="image" src="https://github.com/user-attachments/assets/19e260e9-d96d-4898-b573-170d9b656d0b" />


**Load lại và khởi động:**

```bash
docker load -i bt5_flask.tar
docker-compose up -d
docker ps -a
```

> **Ảnh 19:** Chụp màn hình — thấy:
> - Dòng `Loaded image: bt5_bt5-flask:latest`  
> - 7 container Creating... done  
> - `docker ps -a` hiển thị 7 container đều **Up**  
<img width="1456" height="819" alt="image" src="https://github.com/user-attachments/assets/ddb55d40-5b22-4e76-af96-46dbf18a1755" />


## Kết quả cuối cùng

| Yêu cầu đề bài | Kết quả |
|---|---|
| Node-RED lấy dữ liệu thực tế liên tục | ✅ Mỗi 5 phút lấy giá xăng |
| Lưu vào MariaDB (tức thời) | ✅ Bảng `petrol_price` cập nhật liên tục |
| Lưu vào InfluxDB (lịch sử) | ✅ Bucket `petrol_history` |
| Grafana vẽ biểu đồ | ✅ 3 đường giá DO, RON92, RON95 |
| Nginx + Frontend HTML/JS/CSS | ✅ https://k58-bt5.luongquangha.io.vn |
| Ajax/fetch lấy dữ liệu tức thời | ✅ Mỗi 10 giây tự cập nhật |
| Flask API (giống BT1) | ✅ `/api/petrol` trả JSON |
| Iframe Grafana | ✅ Biểu đồ lịch sử nhúng trong trang |
| Phân loại ngưỡng A..B | ✅ ALERT LOW / OK / ALERT HIGH |
| Telegram Bot alert | ✅ Gửi tin khi vượt ngưỡng |
| Xuất container ra file nén | ✅ `bt5_flask.tar` (49MB) |
| Xóa toàn bộ container | ✅ `docker-compose down` |
| Load lại và khôi phục | ✅ `docker load` + `docker-compose up -d` |

---

## Hướng dẫn chạy lại dự án

```bash
# Clone repo
git clone https://github.com/hluongquang764-web/baitap5.git bt5
cd bt5

# Phân quyền Node-RED
sudo chown -R 1000:1000 ./nodered

# Điền token Cloudflare vào docker-compose.yml
nano docker-compose.yml
# Tìm: PASTE_YOUR_TOKEN_HERE → thay bằng token thật

# Khởi động
docker-compose up -d

# Kiểm tra
docker-compose ps
```

Truy cập:
- **Website:** https://k58-bt5.luongquangha.io.vn
- **Node-RED:** https://k58-bt5.luongquangha.io.vn/nodered/
- **Grafana:** https://k58-bt5.luongquangha.io.vn/grafana/
