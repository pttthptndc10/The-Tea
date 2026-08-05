# 🍵 The Tea - Hệ Thống Quản Lý Dự Án & Công Việc Doanh Nghiệp

[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0+-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://the-tea-eta.vercel.app/)

> **The Tea** là nền tảng quản lý dự án, công việc và tương tác nội bộ doanh nghiệp hiện đại. Nền tảng sở hữu giao diện **Rose Pink & Pearl White** sang trọng, hệ thống xác thực mã OTP 4 chữ số trên 1 trang duy nhất, tính năng nhắn tin trực tiếp tức thời `0ms` chuẩn Zalo và hiệu ứng **Rồng Đông Phương Thần Thoại 2D** tương tác trực quan độc đáo.

---

## 🌐 Trải Nghiệm Trực Tuyến (Live Demo)

- 🔗 **Website Production**: [https://the-tea-eta.vercel.app/](https://the-tea-eta.vercel.app/)
- 📦 **GitHub Repository**: [https://github.com/pttthptndc10/The-Tea.git](https://github.com/pttthptndc10/The-Tea.git)

---

## ✨ Các Tính Năng Nổi Bật

### 🛡️ 1. Hệ Thống Xác Thực & Phân Quyền Bảo Mật
- **Mã OTP 4 Số Gộp 1 Trang**: Trải nghiệm đăng ký và quên mật khẩu tinh gọn. Mã OTP được gửi trực tiếp và xác thực tức thời mà không cần chuyển trang.
- **Phân Quyền Chi Tiết**: Phân biệt vai trò **Admin** (Quản trị viên) và **Member** (Thành viên).
- **Quản Lý Thành Viên (Admin)**: Mời thành viên qua email, khóa/mở khóa tài khoản, đổi vai trò, chuyển quyền Admin.

### 🎨 2. Design System Rose Pink & White Aesthetic
- Tông màu chủ đạo **Hồng Hoa Hồng (Rose Pink `#db2777`, `#be185d`)** kết hợp **Trắng Ngọc (Pearl White `#ffffff`)** thanh lịch.
- Động cơ tạo Avatar tự động lấy ký tự đầu tiên của **Họ tên đăng ký** (Ví dụ: `Nguyễn Văn A` $\rightarrow$ `N`).
- Chuyển tab tức thời `0ms` với hiệu ứng Glassmorphism Skeleton Loader.

### 💬 3. Nhắn Tin Trực Tiếp Real-time Chuẩn Zalo (Direct Messaging)
- **Đẩy tin nhắn tức thời 0ms (Instant Push)**: Gõ Enter hoặc bấm Gửi là tin nhắn hiện ngay trên khung chat mà không hề bị khựng.
- **3 Trạng Thái Tin Nhắn**:
  - 🕒 `Đang gửi...` (Đang truyền dữ liệu tới máy chủ)
  - ✔️ `Đã gửi` (Đã lưu an toàn vào Cơ sở dữ liệu)
  - ✔️✔️ `Đã nhận` (Đối phương đã xem tin nhắn)
- **Đồng bộ siêu nhanh 1.5s**: Tin nhắn hai chiều mượt mà giữa các tài khoản trực tuyến.

### 📁 4. Quản Lý Dự Án & Công Việc (Project & Task Management)
- **Dự Án**: Theo dõi tiến độ hoàn thành %, ngày bắt đầu/kết thúc, Quản lý dự án (Project Manager) và danh sách thành viên tham gia.
- **Nhiệm Vụ (Task)**: Phân công công việc, thiết lập mức độ ưu tiên (Thấp, Trung bình, Cao, Khẩn cấp), hạn chót và cập nhật trạng thái (Chưa bắt đầu, Đang thực hiện, Hoàn thành).

### 🐉 5. Rồng Đông Phương 2D Thần Thoại (Interactive Canvas Engine)
- **Thiết kế Thần Thoại**: Đầu rồng mắt sáng, sừng hươu phân nhánh, bờm rồng uốn lượn và râu rồng ánh kim.
- **Bộ Chi & Móng Vuốt Cơ Bắp (Tứ Trảo Rồng)**: 4 chi cơ bắp khỏe khắn lắc lư, co bóp nhịp nhàng theo sóng thân.
- **Nhịp Bay & Thả Lỏng Trôi Sông**: Rồng tự động chuyển đổi giữa nhịp uốn lượn hình sin mạnh mẽ và nhịp nghỉ trôi êm đềm như trên dòng sông.
- **Tương Tác Cho Rồng Ăn Táo (Feeding Game)**: Click chuột lên nền để tạo quả táo đỏ phát sáng, rồng sẽ tự lướt tới đớp táo và bùng nổ pháo hoa bụi sao.

---

## 📖 Hướng Dẫn Sử Dụng (User Guide)

### 1️⃣ Đăng Ký & Đăng Nhập Tài Khoản
1. Truy cập [https://the-tea-eta.vercel.app/accounts/login/](https://the-tea-eta.vercel.app/accounts/login/)
2. Bấm **Đăng ký tài khoản ngay**.
3. Nhập Email & Họ tên $\rightarrow$ Bấm **Lấy mã OTP**.
4. Nhập 4 chữ số OTP gửi về Email $\rightarrow$ Nhập Mật khẩu mới và bấm **Hoàn tất đăng ký**.

### 2️⃣ Quản Lý Dự Án & Công Việc
1. **Tạo Dự Án**: Vào mục **Dự án** $\rightarrow$ Bấm **Tạo dự án mới** $\rightarrow$ Nhập tên, mô tả, chọn Trưởng dự án và các thành viên.
2. **Gán Nhiệm Vụ**: Vào chi tiết dự án $\rightarrow$ Bấm **Thêm công việc** $\rightarrow$ Chọn người thực hiện, hạn chót và mức độ ưu tiên.

### 3️⃣ Nhắn Tin Trực Tiếp Giữa Các Thành Viên
1. Vào mục **Thành viên** (`/accounts/members/overview/`).
2. Chọn thành viên bạn muốn trao đổi $\rightarrow$ Bấm **Nhắn tin**.
3. Nhập nội dung và ấn **Enter** để gửi tức thì. Xem trạng thái `Đang gửi...` $\rightarrow$ `Đã gửi` $\rightarrow$ `Đã nhận`.

### 4️⃣ Cho Rồng Ăn Táo (Trang Khách)
1. Tại màn hình Đăng nhập / Đăng ký, click chuột vào bất kỳ vùng trống nào trên màn hình.
2. Quả táo đỏ phát sáng sẽ xuất hiện và Rồng Đông Phương sẽ tự động lượn đến đớp táo.

---

## 🛠️ Hướng Dẫn Cài Đặt & Chạy Cục Bộ (Local Setup)

### Yêu Cầu Tiền Đề (Prerequisites)
- **Python 3.10+**
- **Git**

### Các Bước Thực Hiện:

```bash
# 1. Clone mã nguồn từ GitHub
git clone https://github.com/pttthptndc10/The-Tea.git
cd "The Tea"

# 2. Tạo và kích hoạt môi trường ảo Python
python -m venv .venv
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 4. Khởi tạo cơ sở dữ liệu SQLite
python manage.py makemigrations
python manage.py migrate

# 5. Khởi tạo tài khoản Quản trị viên (Superuser)
python manage.py createsuperuser

# 6. Chạy máy chủ phát triển cục bộ
python manage.py runserver
```

Truy cập địa chỉ: `http://127.0.0.1:8000/`

---

## 📂 Cấu Trúc Mã Nguồn (Project Structure)

```text
The Tea/
├── apps/
│   ├── accounts/       # Quản lý User, Roles, OTP, DirectMessage API
│   ├── dashboard/      # Bảng điều khiển trung tâm & Thống kê
│   ├── projects/       # Quản lý Dự án & Thành viên dự án
│   ├── tasks/          # Quản lý Công việc & Trạng thái Kanban
│   ├── notifications/  # Thông báo nội bộ hệ thống
│   ├── purchases/      # Quản lý đơn hàng / mua sắm (nếu có)
│   └── reports/        # Xuất báo cáo thống kê
├── config/
│   ├── settings.py     # Cấu hình Django & Kết nối Supabase PostgreSQL
│   ├── urls.py         # Điểm điều hướng URL chính
│   └── wsgi.py         # Cấu hình WSGI Serverless cho Vercel
├── templates/          # Giao diện HTML5 (TailwindCSS + Jinja2/Django)
│   ├── base.html       # Layout gốc & Canvas Rồng Đông Phương 2D
│   ├── accounts/       # Login, Register, Members Overview, Chat Modal
│   ├── dashboard/      # Trang chủ Dashboard
│   └── projects/       # Giao diện danh sách & chi tiết dự án
├── db.sqlite3          # Cơ sở dữ liệu thử nghiệm cục bộ
├── manage.py           # Trình quản lý lệnh Django
├── requirements.txt    # Danh sách thư viện Python
└── vercel.json         # Cấu hình triển khai tự động trên Vercel
```

---

## 📄 Giấy Phép & Bản Quyền (License)

Dự án thuộc bản quyền của **The Tea Team**. Được phát triển và duy trì bởi đội ngũ Antigravity.
