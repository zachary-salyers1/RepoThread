import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { blog, numTweets } = await request.json()

    if (!blog) {
      return NextResponse.json(
        { error: 'Blog content is required' },
        { status: 400 }
      )
    }

    // Forward the request to the Python FastAPI server
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        blog_content: blog,
        num_tweets: numTweets || 14 // Default to 14 if not specified
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to convert blog to thread')
    }

    return NextResponse.json({ 
      success: true,
      thread: data.thread 
    })

  } catch (error) {
    console.error('Error:', error)
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
} 