functions = [
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a booking via cal.com",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the person booking"},
                    "date": {"type": "string", "description": "Date of the booking"},
                    "time": {"type": "string", "description": "Start time of the booking"},
                    "title": {"type": "string", "description": "Booking title"},
                    "description": {"type": "string", "description": "Booking description"}
                },
                "required": ["name", "date", "time", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_bookings",
            "description": "Find all user bookings via cal.com",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]