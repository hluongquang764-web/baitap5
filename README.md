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

> **Phần B — Thực hành:** Xem thư mục `practice/` — bao gồm `docker-compose.yml`, Node-RED flow, Flask API, frontend HTML/JS và hướng dẫn chạy chi tiết.
