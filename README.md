
# AI Podcast Creator

An automated podcast creation system built with Python and Streamlit that uses AI to generate engaging podcast content.

## Features

- Topic generation and selection
- AI-powered research collection
- Automated script creation
- Content quality checking
- Text-to-speech audio generation
- Social media promotion content generation
- Email distribution system

## Requirements

- Python 3.11+
- Dependencies listed in requirements.txt

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables in `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

Start the Streamlit server:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 5000
```

## Project Structure

- `agents/`: Individual AI agents for different tasks
- `orchestration/`: Workflow management
- `utils/`: Utility functions and helpers
- `audio/`: Generated podcast audio files
- `data/`: User data and podcast storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
