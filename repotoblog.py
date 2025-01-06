import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from typing import Optional
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

class RepoRequest(BaseModel):
    repo_url: str

class RepoResponse(BaseModel):
    blog: str
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
        # Remove markdown code block markers and 'markdown' word
        blog_content = blog_content.replace('```markdown', '').replace('```', '').strip()
        
        return RepoResponse(blog=blog_content, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 