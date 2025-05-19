import httpx
import os
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from .models import BookingRequest

CAL_API_BASE = "https://api.cal.com/v1"
CAL_API_KEY = os.getenv("CAL_API_KEY")
EVENT_TYPE_ID = os.getenv("EVENT_TYPE_ID")

def parse_flexible_time(date_str: str, time_str: str) -> datetime:
    """
    Parse time_str which can be in formats like:
    - "11"
    - "11 AM"
    - "11:00"
    - "11:00 AM"
    Returns a datetime object combining date_str and time_str.
    """
    formats = [
        "%Y-%m-%d %I:%M %p",  # 11:00 AM
        "%Y-%m-%d %I %p",     # 11 AM
        "%Y-%m-%d %H:%M",     # 11:00 (24-hour)
        "%Y-%m-%d %H",        # 11 (24-hour)
    ]

    last_exception = None
    for fmt in formats:
        try:
            return datetime.strptime(f"{date_str} {time_str}", fmt)
        except ValueError as e:
            last_exception = e
            continue

    raise ValueError(f"Time string '{time_str}' does not match any expected formats. Error: {last_exception}")

def combine_datetime_string(date_str: str, time_str: str) -> str:
    dt = parse_flexible_time(date_str, time_str)
    eastern = ZoneInfo("America/New_York")
    local_dt = dt.replace(tzinfo=eastern)
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def build_end_time_string(start_date: str, start_time: str):
    start_dt = parse_flexible_time(start_date, start_time)
    end_dt = start_dt + timedelta(minutes=60)
    eastern = ZoneInfo("America/New_York")
    local_dt = end_dt.replace(tzinfo=eastern)
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def build_url(endpoint: str, params: dict = None):
    base_params = {'apiKey': CAL_API_KEY}
    if params:
        base_params.update(params)
    query = urlencode(base_params)
    return f"{CAL_API_BASE}/{endpoint}?{query}"

async def get_slots(start_time: str, end_time: str):
    url = build_url("slots", {'eventTypeId': EVENT_TYPE_ID, 'startTime': start_time, 'endTime': end_time})
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        slots_data = response.json().get("slots", {});
        total_slots = sum(len(time_slots) for time_slots in slots_data.values())
        if total_slots == 1:
            return True
        return False

async def create_booking(booking: BookingRequest):
    start_time = combine_datetime_string(booking.date, booking.time)
    # assuming that events are of 60 minutes by default
    end_time = build_end_time_string(booking.date, booking.time)
    is_slot_available = await get_slots(start_time, end_time)

    if is_slot_available: 
        payload = {
            "eventTypeId": EVENT_TYPE_ID, ## eventTypeId for 60 minute meetings.
            "start": start_time,
            "end": end_time,
            "responses": {
                "name": booking.name,
                "email": booking.email,
                "notes": "Sample notes",
                "smsReminderNumber": "",
                "location": {
                    "value": "Google Meet",
                    "optionValue": "",
                }
            },
            "timeZone": "America/New_York",
            "language": "en",
            "title": booking.title,
            "description": booking.description if booking.description is not None else "",
            "status": "PENDING",
            "metadata": {}
        }

        url = build_url("bookings")
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("Error response:", e.response.text)

            return {"message": "Booking successfully created"}
    
    return {"message": "No available slot for the requested time."}

async def get_all_user_bookings(user_email: str):
    async with httpx.AsyncClient() as client:
        references_url = build_url("booking-references")
        ref_response = await client.get(references_url)

        try:
            ref_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("Error response:", e.response.text)

        booking_refs = ref_response.json().get("booking_references", [])

        user_bookings = []

        for ref in booking_refs:
            booking_id = ref.get("bookingId")
            if booking_id:
                booking_url = build_url(f"bookings/{booking_id}")
                booking_response = await client.get(booking_url)

                if booking_response.status_code == 200:
                    booking = booking_response.json().get("booking")
                    attendees = booking.get("attendees")
                    for attendee in attendees:
                        if attendee["email"] == user_email:
                            user_bookings.append(booking)
        
        return user_bookings


