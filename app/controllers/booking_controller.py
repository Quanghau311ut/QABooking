import logging
from datetime import datetime

import pyodbc
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import booking

logger = logging.getLogger(__name__)
bookings = Blueprint("bookings", __name__)


@bookings.get("/")
def index():
    selected_date = request.args.get("date", "").strip()
    try:
        parsed_date = datetime.strptime(selected_date, "%Y-%m-%d").date() if selected_date else None
        rooms = booking.get_rooms()
        reservations = booking.get_bookings(parsed_date)
        stats = booking.get_dashboard_stats()
    except ValueError:
        flash("Ngày lọc không hợp lệ.", "error")
        return redirect(url_for("bookings.index"))
    except pyodbc.Error:
        logger.exception("Could not load booking dashboard from SQL Server")
        return render_template("database_error.html"), 503

    return render_template(
        "index.html",
        rooms=rooms,
        bookings=reservations,
        stats=stats,
        selected_date=selected_date,
        today=datetime.now().date().isoformat(),
    )


@bookings.post("/bookings")
def create():
    try:
        room_id = int(request.form.get("room_id", ""))
        attendee_count = int(request.form.get("attendee_count", ""))
        title = request.form.get("title", "").strip()
        organizer = request.form.get("organizer", "").strip()
        department = request.form.get("department", "").strip()
        start_time = datetime.fromisoformat(request.form.get("start_time", ""))
        end_time = datetime.fromisoformat(request.form.get("end_time", ""))

        if not title or not organizer or not department:
            raise ValueError("Vui lòng nhập đầy đủ thông tin cuộc họp.")
        if len(title) > 200 or len(organizer) > 120 or len(department) > 100:
            raise ValueError("Một số thông tin vượt quá độ dài cho phép.")
        if attendee_count < 1:
            raise ValueError("Số người tham dự phải ít nhất là 1.")
        if start_time <= datetime.now():
            raise ValueError("Thời gian bắt đầu phải ở trong tương lai.")
        if end_time <= start_time:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu.")

        booking.create_booking(
            room_id,
            title,
            organizer,
            department,
            start_time,
            end_time,
            attendee_count,
        )
        flash("Đặt phòng họp thành công.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except pyodbc.Error:
        logger.exception("Could not create booking in SQL Server")
        flash("Không thể lưu lịch họp. Vui lòng thử lại sau.", "error")

    return redirect(url_for("bookings.index"))


@bookings.post("/bookings/<int:booking_id>/cancel")
def cancel(booking_id):
    try:
        if booking.cancel_booking(booking_id):
            flash("Đã hủy lịch họp.", "success")
        else:
            flash("Lịch họp không tồn tại hoặc đã được hủy.", "error")
    except pyodbc.Error:
        logger.exception("Could not cancel booking in SQL Server")
        flash("Không thể hủy lịch họp. Vui lòng thử lại sau.", "error")
    return redirect(url_for("bookings.index"))
