from app.models.database import connection_scope


def get_rooms():
    with connection_scope() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT room_id, name, location, capacity, facilities
            FROM dbo.Rooms
            WHERE is_active = 1
            ORDER BY name
            """
        )
        return [
            {
                "id": row.room_id,
                "name": row.name,
                "location": row.location,
                "capacity": row.capacity,
                "facilities": row.facilities,
            }
            for row in cursor.fetchall()
        ]


def get_bookings(search_date=None):
    with connection_scope() as connection:
        cursor = connection.cursor()
        query = """
            SELECT b.booking_id, b.title, b.organizer, b.department,
                   b.start_time, b.end_time, b.attendee_count, b.status,
                   r.name AS room_name, r.location AS room_location
            FROM dbo.Bookings AS b
            INNER JOIN dbo.Rooms AS r ON r.room_id = b.room_id
            WHERE b.status = 'confirmed'
              AND b.end_time >= SYSDATETIME()
        """
        parameters = []
        if search_date:
            query += " AND CONVERT(date, b.start_time) = ?"
            parameters.append(search_date)
        query += " ORDER BY b.start_time"
        cursor.execute(query, parameters)
        return [
            {
                "id": row.booking_id,
                "title": row.title,
                "organizer": row.organizer,
                "department": row.department,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "attendee_count": row.attendee_count,
                "status": row.status,
                "room_name": row.room_name,
                "room_location": row.room_location,
            }
            for row in cursor.fetchall()
        ]


def get_dashboard_stats():
    with connection_scope() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM dbo.Rooms WHERE is_active = 1) AS room_count,
                (SELECT COUNT(*) FROM dbo.Bookings
                 WHERE status = 'confirmed'
                   AND CONVERT(date, start_time) = CONVERT(date, SYSDATETIME()))
                    AS today_count,
                (SELECT COUNT(*) FROM dbo.Bookings
                 WHERE status = 'confirmed' AND end_time >= SYSDATETIME())
                    AS upcoming_count
            """
        )
        row = cursor.fetchone()
        return {
            "room_count": row.room_count,
            "today_count": row.today_count,
            "upcoming_count": row.upcoming_count,
        }


def create_booking(
    room_id, title, organizer, department, start_time, end_time, attendee_count
):
    with connection_scope() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT name, capacity
            FROM dbo.Rooms
            WHERE room_id = ? AND is_active = 1
            """,
            room_id,
        )
        room = cursor.fetchone()
        if room is None:
            raise ValueError("Phòng họp không tồn tại hoặc đã ngừng hoạt động.")
        if attendee_count > room.capacity:
            raise ValueError(
                f"Phòng {room.name} chỉ có sức chứa {room.capacity} người."
            )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.Bookings WITH (UPDLOCK, HOLDLOCK)
            WHERE room_id = ?
              AND status = 'confirmed'
              AND start_time < ?
              AND end_time > ?
            """,
            room_id,
            end_time,
            start_time,
        )
        if cursor.fetchone()[0]:
            raise ValueError("Phòng đã có lịch trong khoảng thời gian này.")

        cursor.execute(
            """
            INSERT INTO dbo.Bookings
                (room_id, title, organizer, department, start_time, end_time,
                 attendee_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')
            """,
            room_id,
            title,
            organizer,
            department,
            start_time,
            end_time,
            attendee_count,
        )
        connection.commit()


def cancel_booking(booking_id):
    with connection_scope() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE dbo.Bookings
            SET status = 'cancelled'
            WHERE booking_id = ? AND status = 'confirmed'
            """,
            booking_id,
        )
        changed = cursor.rowcount
        connection.commit()
        return changed > 0
