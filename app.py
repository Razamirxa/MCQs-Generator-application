from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import YoutubeLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse
import json

load_dotenv()

app = Flask(__name__)

class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question")
    options: List[str] = Field(description="List of possible answers")
    correct_answer: str = Field(description="The correct answer")

class Quiz(BaseModel):
    questions: List[QuizQuestion] = Field(description="List of quiz questions")

def transcribe_youtube_video(url: str) -> str:
    try:
        # Check if the URL is reachable
        response = requests.head(url, timeout=5)
        response.raise_for_status()

        parsed_url = urlparse(url)
        if parsed_url.netloc != 'www.youtube.com' and parsed_url.netloc != 'youtu.be':
            raise ValueError("The provided URL is not a valid YouTube URL")

        print(f"Attempting to transcribe video from URL: {url}")

        loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=False,
            language=["en", "ur", 'hi'],
            translation="en",
        )
        transcription = loader.load()

        if not transcription:
            raise ValueError("No transcription was returned")

        print(f"Successfully transcribed video. Transcription length: {len(transcription[0].page_content)}")
        return transcription[0].page_content
    except requests.exceptions.RequestException as e:
        print(f"Network error when accessing YouTube URL: {str(e)}")
        raise ValueError(f"Failed to access YouTube video: {str(e)}")
    except Exception as e:
        print(f"Error in transcribing YouTube video: {str(e)}")
        raise

def generate_quiz(transcription: str, num_questions: int = 5) -> Quiz:
    model = ChatOpenAI(temperature=0.7, model="gpt-4")
    
    # Create a more structured prompt
    prompt = ChatPromptTemplate.from_template(
        "You are a quiz generator. Your task is to create a multiple-choice quiz based on the provided transcription.\n\n"
        "Instructions:\n"
        "1. Create exactly {num_questions} questions\n"
        "2. Each question must have exactly 4 options\n"
        "3. The correct_answer must match one of the options exactly\n"
        "4. Return ONLY a JSON object with no additional text or formatting\n\n"
        "Required JSON format:\n"
        '{{\n  "questions": [\n    {{\n      "question": "...",\n      "options": ["...", "...", "...", "..."],\n      "correct_answer": "..."\n    }}\n  ]\n}}\n\n'
        "Transcription:\n{transcription}\n\n"
        "Remember: Respond with ONLY the JSON object, no additional text, no markdown formatting."
    )
    
    try:
        # Generate the response
        messages = prompt.format_messages(transcription=transcription, num_questions=num_questions)
        response = model.invoke(messages)
        
        # Clean and validate the response
        content = response.content.strip()
        
        # Debug logging
        print("Raw response content:", repr(content))
        
        # Remove any markdown formatting if present
        if content.startswith("```") and content.endswith("```"):
            content = content[content.find("{"):content.rfind("}")+1]
        elif not (content.startswith("{") and content.endswith("}")):
            # If response doesn't start with { and end with }, try to find JSON object
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != 0:
                content = content[start:end]
            else:
                raise ValueError("Could not find valid JSON object in response")
        
        # Debug logging
        print("Cleaned content:", repr(content))
        
        try:
            quiz_data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Attempted to parse content: {repr(content)}")
            raise ValueError(f"Failed to parse quiz response as JSON: {str(e)}")
        
        # Validate the structure
        if not isinstance(quiz_data, dict):
            raise ValueError("Quiz response is not a dictionary")
        if "questions" not in quiz_data:
            raise ValueError("Quiz response missing 'questions' field")
        if not isinstance(quiz_data["questions"], list):
            raise ValueError("Quiz questions is not a list")
        if len(quiz_data["questions"]) != num_questions:
            raise ValueError(f"Expected {num_questions} questions, got {len(quiz_data['questions'])}")
        
        # Validate each question
        for i, q in enumerate(quiz_data["questions"]):
            if not isinstance(q, dict):
                raise ValueError(f"Question {i+1} is not a dictionary")
            if "question" not in q or "options" not in q or "correct_answer" not in q:
                raise ValueError(f"Question {i+1} missing required fields")
            if not isinstance(q["options"], list) or len(q["options"]) != 4:
                raise ValueError(f"Question {i+1} must have exactly 4 options")
            if q["correct_answer"] not in q["options"]:
                raise ValueError(f"Question {i+1} correct answer must be one of the options")
        
        # Create Quiz object
        return Quiz(**quiz_data)
        
    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        if 'response' in locals():
            print(f"Full response content: {repr(response.content)}")
        raise ValueError(f"Failed to generate quiz: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_route():
    try:
        video_url = request.json.get('video_url', '').strip()
        num_questions = int(request.json.get('num_questions', 5))

        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        if num_questions < 1 or num_questions > 10:
            return jsonify({"error": "Number of questions must be between 1 and 10"}), 400

        transcription = transcribe_youtube_video(video_url)
        if not transcription:
            return jsonify({"error": "Failed to obtain video transcription"}), 400

        quiz = generate_quiz(transcription, num_questions)
        return jsonify({
            "questions": quiz.model_dump()["questions"],
            "transcription": transcription
        })
    except ValueError as e:
        print(f"ValueError in generate_quiz_route: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error in generate_quiz_route: {str(e)}")
        print(f"Full error details: {repr(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8002)