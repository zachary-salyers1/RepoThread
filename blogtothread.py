import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

class BlogRequest(BaseModel):
    blog_content: str
    num_tweets: int = 14  # Default to 14 tweets if not specified

class ThreadResponse(BaseModel):
    thread: str
    success: bool

# Agents
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
    uvicorn.run(app, host="127.0.0.1", port=8001) 