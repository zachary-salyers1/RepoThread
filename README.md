# GitHub to Blog Converter

This application converts GitHub repositories into well-structured blog posts and Twitter threads. It uses Next.js for the frontend and Python FastAPI for the backend, powered by AI to analyze repositories and generate content.

## Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://python.org/) (v3.8 or higher)
- [Git](https://git-scm.com/)

## Environment Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd github-to-blog
```

2. Create and configure environment variables:

Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

Also create a `.env.local` file with the same contents:
```bash
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

## Backend Setup (Python FastAPI)

1. Create and activate a Python virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend services (in separate terminal windows):

Terminal 1 - Repo to Blog Service:
```bash
# Make sure your virtual environment is activated
python repotoblog.py
```

Terminal 2 - Blog to Thread Service:
```bash
# Make sure your virtual environment is activated
python blogtothread.py
```

The backend services will run on:
- Repo to Blog: http://localhost:8000
- Blog to Thread: http://localhost:8001

## Frontend Setup (Next.js)

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the frontend development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Using the Application

1. Open your browser and navigate to http://localhost:3000
2. Enter a GitHub repository URL in the input field
3. Click "Generate Blog Post" to analyze the repository and generate a blog post
4. Once the blog post is generated, you can click "Convert to Thread" to create a Twitter thread

## API Endpoints

### Repo to Blog Service (Port 8000)
- `POST /analyze`
  - Input: `{ "repo_url": "https://github.com/username/repo" }`
  - Output: `{ "blog": "Generated blog content", "success": true }`

### Blog to Thread Service (Port 8001)
- `POST /convert`
  - Input: `{ "blog_content": "Your blog content here" }`
  - Output: `{ "thread": "Generated thread content", "success": true }`

## Troubleshooting

1. **Backend Services Not Starting**
   - Ensure your virtual environment is activated
   - Verify Python dependencies are installed
   - Check if the ports 8000 and 8001 are available

2. **Frontend Not Starting**
   - Ensure Node.js is properly installed
   - Try deleting `node_modules` and running `npm install` again

3. **API Errors**
   - Verify your `.env` and `.env.local` files contain valid API keys
   - Check if both backend services are running
   - Ensure the GitHub repository URL is valid and accessible

## Project Structure

```
github-to-blog/
├── src/                  # Frontend source code
│   ├── app/             # Next.js app directory
│   ├── components/      # React components
│   └── lib/            # Utility functions
├── public/              # Static files
├── repotoblog.py        # Repo to Blog backend service
├── blogtothread.py      # Blog to Thread backend service
├── requirements.txt     # Python dependencies
└── package.json         # Node.js dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
