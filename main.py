import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from typing import Optional
import sqlite3
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="RepoThread API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://repothread.vercel.app",  # Your Vercel production domain
        "http://localhost:3000",          # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
def init_db():
    conn = sqlite3.connect('repothread.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            input TEXT NOT NULL,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Request/Response Models
class RepoRequest(BaseModel):
    repo_url: str

class BlogRequest(BaseModel):
    blog_content: str
    num_tweets: int = 14

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobResult(BaseModel):
    status: str
    result: Optional[str] = None

# Agents
repository_analyst = Agent(
    role="Repository Analyst",
    goal="Analyze GitHub repositories and create comprehensive documentation.",
    backstory="""Expert in code analysis and documentation. You analyze repositories by examining their structure,
    code patterns, and documentation. You don't need external tools - just work with the information provided
    in the repository URL and create documentation based on best practices and your expertise.""",
    verbose=True
)

tutorial_writer = Agent(
    role="Tutorial Writer",
    goal="Transform repository analysis into clear tutorials.",
    backstory="""Technical writer specializing in creating tutorials from repository analysis.
    You take the repository information and create step-by-step guides that explain the project's
    purpose, features, and implementation details.""",
    verbose=True
)

seo_specialist = Agent(
    role="SEO Specialist",
    goal="Optimize content for search engines while maintaining technical accuracy.",
    backstory="""SEO expert who enhances content visibility while preserving technical details.
    You optimize titles, headings, and content structure to improve search rankings.""",
    verbose=True
)

blog_post_creator = Agent(
    role="Blog Post Creator",
    goal="Create engaging blog posts from technical content.",
    backstory="""Creative writer who transforms technical documentation into engaging blog posts.
    You maintain technical accuracy while making the content more accessible and interesting.""",
    verbose=True
)

content_analyst = Agent(
    role="Content Analyst",
    goal="Break down the provided blog post into key sections and highlight main points.",
    verbose=True,
    backstory=(
        "An experienced content strategist who excels at identifying core ideas from long-form content. "
        "You're skilled at structuring information to make it easier to consume."
    )
)

thread_writer = Agent(
    role="Thread Writer",
    goal="Write engaging and concise tweets based on the extracted blog sections.",
    verbose=True,
    backstory=(
        "A creative writer who specializes in crafting Twitter threads that capture attention. "
        "You excel at making complex ideas simple and engaging without using hashtags."
    )
)

editor = Agent(
    role="Editor",
    goal="Review and refine the tweets to ensure clarity, flow, and professionalism.",
    verbose=True,
    backstory=(
        "A meticulous editor with a sharp eye for detail. You're dedicated to improving readability and flow "
        "to deliver polished content that's ready for publication."
    )
)

def save_job(job_type: str, input_data: str) -> str:
    job_id = str(uuid.uuid4())
    conn = sqlite3.connect('repothread.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO jobs (id, type, status, input) VALUES (?, ?, ?, ?)',
        (job_id, job_type, 'pending', input_data)
    )
    conn.commit()
    conn.close()
    return job_id

def get_job_status(job_id: str) -> JobResult:
    conn = sqlite3.connect('repothread.db')
    c = conn.cursor()
    c.execute('SELECT status, result FROM jobs WHERE id = ?', (job_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResult(status=row[0], result=row[1])

def update_job_result(job_id: str, result: str):
    conn = sqlite3.connect('repothread.db')
    c = conn.cursor()
    c.execute(
        'UPDATE jobs SET status = ?, result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ('completed', result, job_id)
    )
    conn.commit()
    conn.close()

@app.post("/analyze", response_model=JobResponse)
async def analyze_repository(request: RepoRequest):
    try:
        # Save job to database
        job_id = save_job('analyze', request.repo_url)
        
        # Start background task to process the repository
        # Note: In a production environment, you'd want to use a proper task queue like Celery
        # For now, we'll process it in a separate thread
        import threading
        def process_repo():
            try:
                # Create tasks for the crew
                analyze_repo = Task(
                    description=f"""Create a comprehensive analysis of the repository at {request.repo_url}.
                    Include the following sections:
                    1. Project Overview
                    2. Key Features
                    3. Technical Implementation
                    4. Setup Instructions
                    5. Usage Examples""",
                    agent=repository_analyst
                )

                write_tutorial = Task(
                    description="""Transform the repository analysis into a detailed tutorial.""",
                    agent=tutorial_writer
                )

                optimize_seo = Task(
                    description="""Optimize the tutorial for search engines while preserving technical accuracy.""",
                    agent=seo_specialist
                )

                create_blog = Task(
                    description="""Transform the SEO-optimized tutorial into an engaging blog post.""",
                    agent=blog_post_creator
                )

                # Create and run the crew
                crew = Crew(
                    agents=[repository_analyst, tutorial_writer, seo_specialist, blog_post_creator],
                    tasks=[analyze_repo, write_tutorial, optimize_seo, create_blog],
                    verbose=True
                )

                # Execute the crew's tasks
                result = crew.kickoff()

                # Convert CrewAI output to string
                blog_content = str(result.raw) if hasattr(result, 'raw') else str(result)
                
                # Update job with result
                update_job_result(job_id, blog_content)
            except Exception as e:
                # Update job with error
                update_job_result(job_id, f"Error: {str(e)}")
        
        # Start processing in background
        thread = threading.Thread(target=process_repo)
        thread.start()
        
        return JobResponse(job_id=job_id, status='pending')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert", response_model=JobResponse)
async def convert_to_thread(request: BlogRequest):
    try:
        # Save job to database
        job_id = save_job('convert', request.blog_content)
        
        # Start background task to process the blog
        import threading
        def process_blog():
            try:
                # Create tasks for the crew
                analyze_content = Task(
                    description=f"""Analyze this blog post and break it down into {request.num_tweets} tweets.
                    Blog content to analyze: {request.blog_content}""",
                    agent=content_analyst
                )

                # Create and run the crew
                crew = Crew(
                    agents=[content_analyst],
                    tasks=[analyze_content],
                    verbose=True
                )

                # Execute the crew's tasks
                result = crew.kickoff()

                # Convert CrewAI output to string
                thread_content = str(result.raw) if hasattr(result, 'raw') else str(result)
                
                # Update job with result
                update_job_result(job_id, thread_content)
            except Exception as e:
                # Update job with error
                update_job_result(job_id, f"Error: {str(e)}")
        
        # Start processing in background
        thread = threading.Thread(target=process_blog)
        thread.start()
        
        return JobResponse(job_id=job_id, status='pending')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobResult)
async def get_job(job_id: str):
    return get_job_status(job_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 