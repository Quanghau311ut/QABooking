IF DB_ID(N'QABooking') IS NULL
BEGIN
    CREATE DATABASE QABooking;
END;
GO

USE QABooking;
GO

IF OBJECT_ID(N'dbo.Rooms', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Rooms (
        room_id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Rooms PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        location NVARCHAR(150) NOT NULL,
        capacity INT NOT NULL,
        facilities NVARCHAR(500) NOT NULL CONSTRAINT DF_Rooms_Facilities DEFAULT N'',
        is_active BIT NOT NULL CONSTRAINT DF_Rooms_IsActive DEFAULT 1,
        CONSTRAINT CK_Rooms_Capacity CHECK (capacity > 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.Bookings', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Bookings (
        booking_id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Bookings PRIMARY KEY,
        room_id INT NOT NULL,
        title NVARCHAR(200) NOT NULL,
        organizer NVARCHAR(120) NOT NULL,
        department NVARCHAR(100) NOT NULL,
        start_time DATETIME2(0) NOT NULL,
        end_time DATETIME2(0) NOT NULL,
        attendee_count INT NOT NULL,
        status VARCHAR(20) NOT NULL CONSTRAINT DF_Bookings_Status DEFAULT 'confirmed',
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_Bookings_CreatedAt DEFAULT SYSDATETIME(),
        CONSTRAINT FK_Bookings_Rooms FOREIGN KEY (room_id) REFERENCES dbo.Rooms(room_id),
        CONSTRAINT CK_Bookings_Time CHECK (end_time > start_time),
        CONSTRAINT CK_Bookings_Attendees CHECK (attendee_count > 0),
        CONSTRAINT CK_Bookings_Status CHECK (status IN ('confirmed', 'cancelled'))
    );
    CREATE INDEX IX_Bookings_Room_Time
        ON dbo.Bookings(room_id, status, start_time, end_time);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Rooms)
BEGIN
    INSERT INTO dbo.Rooms (name, location, capacity, facilities)
    VALUES
        (N'Phòng Sáng Tạo', N'Tầng 3 · Khu A', 8, N'Màn hình 4K, Bảng viết'),
        (N'Phòng Cộng Hưởng', N'Tầng 5 · Khu B', 12, N'Máy chiếu, Video conference'),
        (N'Phòng Hội Nghị', N'Tầng 6 · Khu A', 20, N'Màn hình lớn, Loa hội nghị');
END;
GO
