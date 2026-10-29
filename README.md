# QABooking

Ứng dụng web đặt phòng họp nội bộ, xây dựng bằng Python/Flask theo mô hình MVC và sử dụng Microsoft SQL Server.

## Công nghệ và cấu trúc

- **Model:** `app/models/` — truy vấn và ghi dữ liệu SQL Server bằng `pyodbc`.
- **View:** `app/templates/` và `app/static/` — giao diện Jinja/HTML/CSS.
- **Controller:** `app/controllers/` — xử lý trang tổng quan, tạo và hủy lịch đặt.
- **Database:** `database/schema.sql` — tạo bảng phòng họp, lịch đặt và dữ liệu phòng mẫu.

Ứng dụng hỗ trợ xem lịch sắp tới, lọc theo ngày, đặt phòng, kiểm tra sức chứa và ngăn lịch trùng trong cùng phòng.

## Chạy trên Windows

1. Cài Python 3.10 trở lên, SQL Server (hoặc SQL Server Express) và **Microsoft ODBC Driver 18 for SQL Server**.
2. Mở SQL Server Management Studio, chạy toàn bộ `database/schema.sql` bằng tài khoản có quyền tạo database.
3. Tạo môi trường và cài dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Thiết lập kết nối. Ví dụ dùng SQL Authentication:

   ```powershell
   $env:SQL_SERVER = "localhost"
   $env:SQL_DATABASE = "QABooking"
   $env:SQL_USER = "sa"
   $env:SQL_PASSWORD = "your-password"
   ```

   Hoặc dùng Windows Authentication bằng cách bỏ `SQL_USER` và `SQL_PASSWORD`. Có thể cấu hình đầy đủ bằng biến `SQL_CONNECTION_STRING`; mặc định ứng dụng dùng `localhost`, database `QABooking`, ODBC Driver 18 và Windows Authentication.

5. Khởi chạy:

   ```powershell
   python app.py
   ```

   Mở `http://127.0.0.1:5000`.

Có thể đặt `SECRET_KEY` cho session và `FLASK_DEBUG=true` khi phát triển. Không bật debug hoặc dùng khóa mặc định khi triển khai thật.
