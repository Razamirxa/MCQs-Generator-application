from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import YoutubeLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

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
    model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini") # that is correct model do not change it
    structured_llm = model.with_structured_output(Quiz)

    prompt = ChatPromptTemplate.from_template(
        "Based on the following video transcription, generate a quiz with {num_questions} multiple-choice questions. "
        "Each question should have 4 options, with one correct answer. "
        "Ensure the questions cover key points from the video content.\n\n"
        "Transcription:\n{transcription}\n\n"
    )

    result = structured_llm.invoke(prompt.format_messages(transcription=transcription, num_questions=num_questions)[0].content)

    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_route():
    video_url = request.json['video_url']
    num_questions = int(request.json['num_questions'])

    try:
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
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8002)