import { NextResponse } from 'next/server'

export const maxDuration = 300 // Set maximum duration to 300 seconds (5 minutes)
export const dynamic = 'force-dynamic' // Disable static optimization

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
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 290000) // 290 seconds timeout

    const response = await fetch(`${apiUrl}/convert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        blog_content: blog,
        num_tweets: numTweets || 14 // Default to 14 if not specified
      }),
      signal: controller.signal
    }).finally(() => {
      clearTimeout(timeoutId)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      throw new Error(errorData?.detail || 'Failed to convert blog to thread')
    }

    const data = await response.json()

    return NextResponse.json({ 
      success: true,
      thread: data.thread 
    })

  } catch (error) {
    console.error('Error:', error)
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timed out. The conversion is taking longer than expected.' },
        { status: 504 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
} 