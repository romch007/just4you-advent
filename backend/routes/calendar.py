import os
import zipfile
from io import BytesIO
from flask import Blueprint, current_app, send_file, request, jsonify

from middlewares import admin_required, token_required
from models import Calendar, CalendarDay, User

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/calendars", methods=["POST"])
@admin_required
def create_calendar():
    # Check if name and file are present
    if "name" not in request.form:
        return jsonify({"error": "Calendar name is required"}), 400

    if "images" not in request.files:
        return jsonify({"error": "Images zip file is required"}), 400

    name = request.form["name"]
    zip_file = request.files["images"]

    # Validate zip file
    if not zip_file.filename.endswith(".zip"):
        return jsonify({"error": "File must be a zip archive"}), 400

    Session = current_app.config["DB_SESSION"]

    session = Session()
    try:
        # Create calendar
        calendar = Calendar(name=name)
        session.add(calendar)
        session.flush()  # Get calendar.id without committing

        # Create calendar directory
        calendar_dir = os.path.join(
            current_app.config["UPLOAD_FOLDER"], str(calendar.id)
        )
        os.makedirs(calendar_dir, exist_ok=True)

        # Extract and process zip file
        zip_data = BytesIO(zip_file.read())

        with zipfile.ZipFile(zip_data, "r") as zip_ref:
            # Get all PNG files
            png_files = [f for f in zip_ref.namelist() if f.endswith(".png")]

            # Check we have exactly 24 images
            day_images = {}
            for filename in png_files:
                # Extract day number from filename (e.g., "1.png" -> 1)
                basename = os.path.basename(filename)
                try:
                    day_num = int(basename.replace(".png", ""))
                    if 1 <= day_num <= 24:
                        day_images[day_num] = filename
                except ValueError:
                    continue

            if len(day_images) != 24:
                return (
                    jsonify(
                        {
                            "error": f"Zip must contain exactly 24 images named 1.png through 24.png. Found {len(day_images)} valid images"
                        }
                    ),
                    400,
                )

            # Extract images and create calendar days
            for day_num in range(1, 25):
                if day_num not in day_images:
                    return jsonify({"error": f"Missing image for day {day_num}"}), 400

                # Extract image
                image_filename = day_images[day_num]
                image_data = zip_ref.read(image_filename)

                # Save image
                image_path = os.path.join(calendar_dir, f"{day_num}.png")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)

                # Create calendar day
                calendar_day = CalendarDay(
                    day=day_num,
                    image_path=image_path,
                    is_open=False,
                    calendar_id=calendar.id,
                )
                session.add(calendar_day)

        session.commit()

        # Return created calendar with days
        calendar_days = (
            session.query(CalendarDay)
            .filter_by(calendar_id=calendar.id)
            .order_by(CalendarDay.day)
            .all()
        )

        return (
            jsonify(
                {
                    "message": "Calendar created successfully",
                    "calendar": {
                        "id": calendar.id,
                        "name": calendar.name,
                        "days": [
                            {"id": day.id, "day": day.day, "is_open": day.is_open}
                            for day in calendar_days
                        ],
                    },
                }
            ),
            201,
        )

    except Exception as e:
        session.rollback()
        # Clean up created directory if exists
        calendar_dir = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            str(calendar.id) if "calendar" in locals() else "tmp",
        )
        if os.path.exists(calendar_dir):
            import shutil

            shutil.rmtree(calendar_dir)
        return jsonify({"error": f"Failed to create calendar: {str(e)}"}), 500
    finally:
        session.close()


@calendar_bp.route("/calendars/<int:calendar_id>", methods=["GET"])
@admin_required
def get_calendar(calendar_id):
    Session = current_app.config["DB_SESSION"]

    session = Session()
    try:
        calendar = session.query(Calendar).filter_by(id=calendar_id).first()

        if not calendar:
            return jsonify({"error": "Calendar not found"}), 404

        calendar_days = (
            session.query(CalendarDay)
            .filter_by(calendar_id=calendar.id)
            .order_by(CalendarDay.day)
            .all()
        )

        return (
            jsonify(
                {
                    "id": calendar.id,
                    "name": calendar.name,
                    "days": [
                        {"id": day.id, "day": day.day, "is_open": day.is_open}
                        for day in calendar_days
                    ],
                }
            ),
            200,
        )

    finally:
        session.close()


@calendar_bp.route("/my-calendar", methods=["GET"])
@token_required
def get_my_calendar():
    Session = current_app.config["DB_SESSION"]

    session = Session()
    try:
        user = session.query(User).filter_by(id=request.current_user["user_id"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        calendar = session.query(Calendar).filter_by(id=user.calendar_id).first()

        if not calendar:
            return jsonify({"error": "Calendar not found"}), 404

        calendar_days = (
            session.query(CalendarDay)
            .filter_by(calendar_id=calendar.id)
            .order_by(CalendarDay.day)
            .all()
        )

        return (
            jsonify(
                {
                    "id": calendar.id,
                    "name": calendar.name,
                    "days": [
                        {"id": day.id, "day": day.day, "is_open": day.is_open}
                        for day in calendar_days
                    ],
                }
            ),
            200,
        )

    finally:
        session.close()


@calendar_bp.route("/images/<int:day>", methods=["GET"])
@token_required
def get_image(day):
    if day < 1 or day > 24:
        return jsonify({"error": "Day must be between 1 and 24"}), 400

    Session = current_app.config["DB_SESSION"]

    session = Session()
    try:
        user = session.query(User).filter_by(id=request.current_user["user_id"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        calendar_day = (
            session.query(CalendarDay)
            .filter_by(calendar_id=user.calendar_id, day=day)
            .first()
        )

        if not calendar_day:
            return jsonify({"error": f"Day {day} not found in calendar"}), 404

        # TODO: check if calendar_day is open

        if not calendar_day.image_path or not os.path.exists(calendar_day.image_path):
            return jsonify({"error": "Image not found"}), 404

        return send_file(calendar_day.image_path, mimetype="image/png")

    finally:
        session.close()
