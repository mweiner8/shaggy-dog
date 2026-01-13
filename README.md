# 🐕 Shaggy Dog

Transform your headshot into your dog doppelganger!

**Live Demo**: [shaggydob.online](https://shaggydob.online)

## Features

- 🔍 **AI-Powered Breed Detection** - Uses GPT-4o-mini to identify which dog breed you most resemble
- 🎨 **Progressive Transformation** - Watch your photo gradually transform through 2 transition stages
- 🖼️ **Image Gallery** - Save and view all your transformations
- 🔐 **Secure Authentication** - User accounts with encrypted passwords
- ⚡ **Real-time Progress** - Live progress bar showing transformation status

## Technology Stack

- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL
- **AI/ML**: OpenAI (GPT-4o-mini, DALL-E 3)
- **Authentication**: Flask-Login with bcrypt
- **Frontend**: Bootstrap 5, JavaScript
- **Deployment**: Render

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/shaggy-dog.git
cd shaggy-dog
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/shaggydog
OPENAI_API_KEY=sk-your-openai-key-here
FLASK_ENV=development
```

5. Initialize database:
```bash
python init_db.py
```

6. Run the application:
```bash
python run.py
```

7. Visit `http://localhost:5000`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Render.

## Project Structure

```
shaggy-dog/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── routes/              # Route blueprints
│   ├── services/            # OpenAI integration
│   ├── utils/               # Helper functions
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
├── config.py                # Configuration
├── run.py                   # Development server
├── requirements.txt         # Python dependencies
└── README.md
```

## API Costs

Each transformation costs approximately:
- GPT-4o-mini (breed identification): ~$0.002
- DALL-E 3 (3 images): ~$0.12
- **Total per transformation**: ~$0.12

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [OpenAI](https://openai.com/)
- Deployed on [Render](https://render.com/)

## Support

For issues or questions, please open an issue on GitHub.

---

Made with ❤️ and AI