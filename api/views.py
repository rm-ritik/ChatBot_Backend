from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BookingRequest
from .openai_functions import functions 
from .cal_api import create_booking, get_all_user_bookings

from openai import OpenAI
import os
import json
import asyncio

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatAPIView(APIView):
    def post(self, request):
        user_email = request.data.get("email")
        message = request.data.get("message")
        if not user_email or not message:
            return Response({"error": "email and message required"}, status=status.HTTP_400_BAD_REQUEST)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant managing calendar bookings via Cal.com."},
                {"role": "user", "content": message}
            ],
            tools=functions,
            tool_choice="auto"
            )
        message_response = response.choices[0].message

        if message_response.tool_calls and len(message_response.tool_calls) > 0:
            tool_call = message_response.tool_calls[0]
            function_name = tool_call.function.name
            arguments_json = tool_call.function.arguments
            if function_name == 'create_booking':
                try:
                    function_args = json.loads(arguments_json)
                    function_args["email"] = user_email
                    booking = BookingRequest(**function_args)
                except json.JSONDecodeError:
                    return Response({"reply": "Could not parse arguments."})

                booking_result = asyncio.run(create_booking(booking))
                return Response({"reply": booking_result})
            elif function_name == 'find_bookings':
                bookings = asyncio.run(get_all_user_bookings(user_email))
                return Response({"reply": bookings})
                    
        return Response({"reply": message_response.content or "Sorry, some internal error occured."})

