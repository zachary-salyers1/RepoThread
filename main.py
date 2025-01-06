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

@app.post("/analyze", response_model=RepoResponse)
async def analyze_repository(request: RepoRequest):
    try:
        # Create tasks for the crew
        analyze_repo = Task(
            description=f"""Create a comprehensive analysis of the repository at {request.repo_url}.
            
            Include the following sections:
            1. Project Overview
            2. Key Features
            3. Technical Implementation
            4. Setup Instructions
            5. Usage Examples
            
            Base your analysis on standard GitHub repository structures and best practices.
            Focus on creating valuable documentation that helps users understand the project.""",
            agent=repository_analyst
        )

        write_tutorial = Task(
            description="""Transform the repository analysis into a detailed tutorial.
            
            Structure the tutorial with:
            1. Introduction
            2. Prerequisites
            3. Installation Steps
            4. Usage Guide
            5. Code Examples
            6. Best Practices
            7. Troubleshooting
            
            Make it easy to follow while maintaining technical accuracy.""",
            agent=tutorial_writer
        )

        optimize_seo = Task(
            description="""Optimize the tutorial for search engines while preserving technical accuracy.
            
            Focus on:
            1. Title optimization
            2. Header structure
            3. Keyword placement
            4. Meta description
            5. Content organization
            
            Ensure the technical content remains accurate and valuable.""",
            agent=seo_specialist
        )

        create_blog = Task(
            description="""Transform the SEO-optimized tutorial into an engaging blog post.
            
            Include:
            1. Engaging introduction
            2. Clear sections
            3. Code examples
            4. Practical tips
            5. Conclusion with next steps
            
            Make it interesting while keeping the technical details accurate.""",
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