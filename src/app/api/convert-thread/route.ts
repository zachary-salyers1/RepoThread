import { NextResponse } from 'next/server'

export const maxDuration = 60 // Set maximum duration to 60 seconds (Vercel Hobby plan limit)
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
    const timeoutId = setTimeout(() => controller.abort(), 55000) // 55 seconds timeout

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
        { error: 'Request timed out. Please try again with a shorter blog post or upgrade to a plan with longer timeouts.' },
        { status: 504 }
      )
    }
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
} 