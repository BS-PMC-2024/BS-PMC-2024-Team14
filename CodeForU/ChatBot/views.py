from django.shortcuts import render,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from users.decorators import mentor_required
from django.contrib.auth.decorators import login_required
from .models import Question
from django.shortcuts import render
from django.http import JsonResponse
import openai
from dotenv import load_dotenv
from django.shortcuts import redirect
load_dotenv()

@mentor_required
@csrf_exempt
def chat_page(request):
    client = OpenAI()
    response_message = None
    user_id = request.user.id
    session_key = f'conversation_{user_id}'

    if session_key not in request.session:
        request.session[session_key] = [
            {"role": "system", "content": "Respond directly with the answer or code without any prefacing text."}
        ]
    conversation = request.session[session_key ]
    

    if request.method == "POST":
        user_input = request.POST.get('message')

        if user_input.lower() == "clear chat":
            request.session[session_key] = [
                {"role": "system", "content": "Respond directly with the answer or code without any prefacing text."}
            ]
            conversation = []
            response_message = "Chat has been cleared."
        else:
            try:
                # Append user input to the conversation
                conversation.append({"role": "user", "content": user_input})

                # Create a chat completion
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation
                )
                
                response_message = response.choices[0].message.content
                
                # Check if the response contains code
                if "write code" in user_input.lower() or "write some code" in user_input.lower() or  "solve in code" in user_input.lower():
                    # Assume code is returned if user asks to write code
                    response_message = f"```c\n{response_message}\n```"

                # Append assistant's response to the conversation
                conversation.append({"role": "assistant", "content": response_message})
                request.session[session_key] = conversation
                return JsonResponse({
                'user_message': user_input,
                'assistant_message': response_message
            })

            except openai.error.InvalidRequestError as e:
                if e.code == 'insufficient_quota':
                    response_message = "You have exceeded your current quota. Please check your plan and billing details."
                else:
                    response_message = f"OpenAI API error: {e}"
            except Exception as e:
                response_message = f"An error occurred: {e}"
        return redirect('chat_page')
    filtered_conversation = [msg for msg in conversation if msg["role"] != "system"]
    return render(request, 'AskQ.html', {'conversation': filtered_conversation})

def test_openai_api(request):
    # Set up OpenAI API key
    client = OpenAI()
    try:
        # Make a simple request to test the API key
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "what is 5+4"}
            ]
        )

        # Access the response message
        test_message = response.choices[0].message.content
        return JsonResponse({"message": test_message})

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {e}"})


@csrf_exempt
def save_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        level = request.POST.get('level')
        user_id = request.user.id  # Manually set the user ID
        q = Question.objects.create(user=user_id, question_text=question_text, level=level)
        q.original_question_id = q.id
        q.save()
        return redirect('chat_page')