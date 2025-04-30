# YouTube Lecture Quiz Generator

A modern web application that automatically generates interactive quizzes from YouTube video content using AI. Perfect for educators, students, and self-learners who want to test their understanding of video lectures.

![Quiz Generator Screenshot](static/presentation%20(1).png)

## Features

- 🎥 Generate quizzes from any YouTube video
- 🤖 AI-powered question generation
- 📝 Multiple-choice question format
- 🌗 Dark/Light theme support
- 📊 Progress tracking
- 📱 Responsive design
- 📋 View video transcription
- 🔗 Social sharing integration
- 📈 Instant quiz results and feedback

## Technologies Used

- **Backend:**
  - Flask (Python web framework)
  - LangChain (AI/LLM integration)
  - OpenAI GPT-4 (Quiz generation)
  - YouTube API (Video transcription)

- **Frontend:**
  - HTML5
  - CSS3 (Modern design with CSS variables)
  - JavaScript (ES6+)
  - Font Awesome (Icons)
  - Google Fonts

## Setup and Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Quiz_Generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
OPENAI_API_KEY=your_openai_api_key
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:8002`

## Usage

1. Enter a YouTube video URL in the input field
2. Select the number of questions you want (1-10)
3. Click "Generate Quiz"
4. Answer the multiple-choice questions
5. Submit your answers to see your results
6. Share your score on social media (optional)
7. View the video transcription if needed

## Features in Detail

### Quiz Generation
- Automatically extracts key concepts from video content
- Generates relevant multiple-choice questions
- Provides immediate feedback on answers

### User Interface
- Clean, modern design
- Dark/Light theme toggle
- Progress tracking bar
- Responsive layout for all devices
- Animated loading states
- Error handling with user-friendly messages

### Accessibility
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast color schemes
- Responsive text sizing

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4 API
- YouTube API for video transcription
- Font Awesome for icons
- Google Fonts for typography

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by [Your Name] 