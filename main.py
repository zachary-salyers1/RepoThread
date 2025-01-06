import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from typing import Optional

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

# Request/Response Models
class RepoRequest(BaseModel):
    repo_url: str

class BlogRequest(BaseModel):
    blog_content: str
    num_tweets: int = 14  # Default to 14 tweets if not specified

class RepoResponse(BaseModel):
    blog: str
    success: bool

class ThreadResponse(BaseModel):
    thread: str
    success: bool

# Agents
repository_analyst = Agent(
    role="Repository Analyst",
    goal="Analyze GitHub repositories and document insights.",
    backstory="Expert in code analysis and repository breakdowns.",
    verbose=True
)

tutorial_writer = Agent(
    role="Tutorial Writer",
    goal="Write structured tutorials for repositories.",
    backstory="Technical writer skilled at simplifying complex concepts.",
    verbose=True
)

seo_specialist = Agent(
    role="SEO Specialist",
    goal="Optimize tutorial content for SEO without changing the technical focus.",
    backstory="SEO expert focused on enhancing readability without sacrificing technical accuracy.",
    verbose=True
)

blog_post_creator = Agent(
    role="Blog Post Creator",
    goal="Adapt tutorials into engaging, SEO-compliant blog posts with a focus on the repository's purpose and features.",
    backstory="Creative writer with experience in blog formatting without losing technical details.",
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

@app.post("/analyze", response_model=RepoResponse)
async def analyze_repository(request: RepoRequest):
    try:
        # Create tasks for the crew
        analyze_repo = Task(
            description=f"Analyze the GitHub repository at {request.repo_url}. Focus on understanding its purpose, main features, and technical implementation. Repository URL: {request.repo_url}",
            agent=repository_analyst
        )

        write_tutorial = Task(
            description="Write a detailed tutorial based on the repository analysis. Include code examples and explanations.",
            agent=tutorial_writer
        )

        optimize_seo = Task(
            description="Optimize the tutorial content for SEO while maintaining technical accuracy.",
            agent=seo_specialist
        )

        create_blog = Task(
            description="Transform the SEO-optimized tutorial into a well-structured blog post.",
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
        
        return RepoResponse(blog=blog_content, success=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert", response_model=ThreadResponse)
async def convert_to_thread(request: BlogRequest):
    try:
        # Create tasks for the crew
        analyze_content = Task(
            description=f"""Analyze this blog post and break it down into {request.num_tweets} tweets. 
            Focus on maintaining coherence while fitting Twitter's character limit.
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
        
        return ThreadResponse(thread=thread_content, success=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 