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

@app.post("/analyze")
async def analyze_repository(request: RepoRequest) -> RepoResponse:
    try:
        # Tasks
        analyze_repository_task = Task(
            description=f"Analyze the repository at {request.repo_url} to extract structure, features, and purpose.",
            expected_output="Detailed insights into the repository, including code snippets.",
            agent=repository_analyst,
        )

        write_tutorial_task = Task(
            description="Draft a step-by-step tutorial based on the repository analysis. Ensure examples highlight repository usage.",
            expected_output="A markdown-formatted tutorial with setup and usage details.",
            agent=tutorial_writer,
        )

        seo_optimization_task = Task(
            description="Optimize the tutorial for SEO by adding keywords, headings, and metadata, ensuring no technical details are lost.",
            expected_output="An SEO-optimized tutorial ready for publishing, preserving technical accuracy.",
            agent=seo_specialist,
        )

        format_blog_post_task = Task(
            description="Adapt the tutorial into an SEO-friendly blog post with repository-focused narratives and examples.",
            expected_output="A markdown-formatted blog post, ready for publishing, that highlights the repository's features and use cases.",
            agent=blog_post_creator,
        )

        # Crew
        crew = Crew(
            agents=[repository_analyst, tutorial_writer, seo_specialist, blog_post_creator],
            tasks=[
                analyze_repository_task,
                write_tutorial_task,
                seo_optimization_task,
                format_blog_post_task,
            ],
            process=Process.sequential
        )

        # Execute
        result = crew.kickoff(inputs={"repo_url": request.repo_url})
        
        # Convert CrewAI output to string and clean up markdown formatting
        blog_content = str(result.raw) if hasattr(result, 'raw') else str(result)
        # Remove markdown code block markers and clean up
        blog_content = blog_content.replace('```markdown', '').replace('```', '').strip()
        
        return RepoResponse(blog=blog_content, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert")
async def convert_to_thread(request: BlogRequest) -> ThreadResponse:
    try:
        # Tasks
        analyze_blog_task = Task(
            description=(
                f"Analyze the following blog post and break it into key sections with main ideas. "
                f"The final thread should be approximately {request.num_tweets} tweets long.\n\n"
                f"BLOG CONTENT:\n{request.blog_content}"
            ),
            expected_output="A structured summary of the specific blog post provided, with key points and highlights.",
            agent=content_analyst
        )

        write_thread_task = Task(
            description=(
                f"Using the analysis provided, create a Twitter thread of approximately {request.num_tweets} tweets. "
                "Write each tweet clearly and concisely, keeping the thread engaging without hashtags. "
                "Use actual content and examples from the blog post."
            ),
            expected_output="A series of tweets that accurately represent the provided blog content.",
            agent=thread_writer
        )

        edit_thread_task = Task(
            description=(
                f"Review the drafted tweets and ensure they accurately reflect the original blog content. "
                f"The thread should be approximately {request.num_tweets} tweets long. "
                "Refine their structure, language, and transitions while maintaining the original message."
            ),
            expected_output="A finalized Twitter thread that faithfully represents the original blog post.",
            agent=editor
        )

        # Crew Setup
        crew = Crew(
            agents=[content_analyst, thread_writer, editor],
            tasks=[analyze_blog_task, write_thread_task, edit_thread_task],
            process=Process.sequential
        )

        # Execute with the blog content
        result = crew.kickoff(
            inputs={
                'blog_content': request.blog_content
            }
        )
        
        # Convert CrewOutput to string and clean up formatting
        thread_content = str(result.raw) if hasattr(result, 'raw') else str(result)
        # Remove any markdown code block markers if present
        thread_content = thread_content.replace('```markdown', '').replace('```', '').strip()
        
        return ThreadResponse(thread=thread_content, success=True)
    except Exception as e:
        print(f"Error processing blog to thread: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to convert blog to thread: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 