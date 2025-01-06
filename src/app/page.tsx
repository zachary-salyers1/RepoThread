'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [blog, setBlog] = useState<string | null>(null)
  const [thread, setThread] = useState<string | null>(null)
  const [threadLoading, setThreadLoading] = useState(false)
  const [numTweets, setNumTweets] = useState(14)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setBlog(null)
    setThread(null)

    const formData = new FormData(e.currentTarget)
    const repoUrl = formData.get('repo-url')

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repoUrl }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze repository')
      }

      setBlog(data.blog)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const handleThreadGeneration = async () => {
    if (!blog) return
    
    setThreadLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/convert-thread', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          blog,
          numTweets 
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate thread')
      }

      setThread(data.thread)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate thread')
    } finally {
      setThreadLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">GitHub to Blog & Thread Converter</h1>
        
        <div className="bg-white/5 p-8 rounded-lg backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="repo-url" 
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                GitHub Repository URL
              </label>
              <input
                type="url"
                id="repo-url"
                name="repo-url"
                className="w-full px-4 py-2 bg-black/20 border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://github.com/username/repository"
                required
                disabled={loading}
              />
            </div>
            
            <Button 
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Generating Blog...' : 'Generate Blog Post'}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-md text-red-500">
              {error}
            </div>
          )}

          {blog && (
            <div className="mt-8">
              <h2 className="text-xl font-bold mb-4">Generated Blog Post</h2>
              <div className="bg-black/20 p-4 rounded-md whitespace-pre-wrap">
                {blog}
              </div>
              <div className="flex gap-2 mt-4">
                <Button
                  onClick={() => {
                    navigator.clipboard.writeText(blog)
                  }}
                  variant="secondary"
                >
                  Copy Blog
                </Button>
                <div className="flex items-center gap-2">
                  <label 
                    htmlFor="num-tweets" 
                    className="text-sm font-medium text-gray-300"
                  >
                    Number of Tweets:
                  </label>
                  <input
                    type="number"
                    id="num-tweets"
                    min="5"
                    max="50"
                    value={numTweets}
                    onChange={(e) => setNumTweets(Number(e.target.value))}
                    className="w-20 px-2 py-1 bg-black/20 border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <Button 
                  onClick={handleThreadGeneration}
                  disabled={threadLoading}
                >
                  {threadLoading ? 'Converting to Thread...' : 'Convert to Thread'}
                </Button>
              </div>
            </div>
          )}

          {thread && (
            <div className="mt-8">
              <h2 className="text-xl font-bold mb-4">Generated Thread</h2>
              <div className="bg-black/20 p-4 rounded-md whitespace-pre-wrap">
                {thread}
              </div>
              <Button
                onClick={() => {
                  navigator.clipboard.writeText(thread)
                }}
                className="mt-4"
                variant="secondary"
              >
                Copy Thread
              </Button>
            </div>
          )}
          
          {!blog && !error && (
            <div className="mt-8 text-sm text-gray-400">
              <h2 className="font-medium mb-2">How it works:</h2>
              <ol className="list-decimal list-inside space-y-2">
                <li>Enter a GitHub repository URL</li>
                <li>Our AI will analyze the repository and create a blog post</li>
                <li>Review and edit the generated blog post</li>
                <li>Convert the blog post into a Twitter thread</li>
                <li>Review and publish your content</li>
              </ol>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
