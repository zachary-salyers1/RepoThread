'use client'

import { useState } from 'react'

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('')
  const [blog, setBlog] = useState('')
  const [thread, setThread] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [jobId, setJobId] = useState('')
  const [progress, setProgress] = useState<string>('')

  const pollJobStatus = async (id: string, type: 'analyze' | 'convert') => {
    try {
      const endpoint = type === 'analyze' ? '/api/analyze' : '/api/convert-thread'
      const response = await fetch(`${endpoint}?jobId=${id}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get job status')
      }

      if (data.status === 'completed') {
        setLoading(false)
        setProgress('')
        if (type === 'analyze') {
          setBlog(data.result)
        } else {
          setThread(data.result)
        }
        setJobId('')
        return true
      } else if (data.status === 'pending') {
        // Update progress message
        setProgress(type === 'analyze' ? 'Analyzing repository...' : 'Converting to thread...')
        // Continue polling
        setTimeout(() => pollJobStatus(id, type), 5000)
        return false
      } else {
        throw new Error('Job failed: ' + data.result)
      }
    } catch (err) {
      setLoading(false)
      setProgress('')
      setError(err instanceof Error ? err.message : String(err))
      setJobId('')
      return true
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setProgress('Starting analysis...')
    setBlog('')
    setThread('')

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

      setJobId(data.job_id)
      pollJobStatus(data.job_id, 'analyze')
    } catch (err) {
      setLoading(false)
      setProgress('')
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  const handleConvertToThread = async () => {
    if (!blog) return
    setError('')
    setLoading(true)
    setProgress('Starting conversion...')
    setThread('')

    try {
      const response = await fetch('/api/convert-thread', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ blog }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to convert blog to thread')
      }

      setJobId(data.job_id)
      pollJobStatus(data.job_id, 'convert')
    } catch (err) {
      setLoading(false)
      setProgress('')
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  const handleCopyBlog = async () => {
    try {
      await navigator.clipboard.writeText(blog)
      setError('Blog content copied to clipboard!')
      setTimeout(() => setError(''), 3000)
    } catch (err) {
      setError('Failed to copy blog content')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleCopyThread = async () => {
    try {
      await navigator.clipboard.writeText(thread)
      setError('Thread content copied to clipboard!')
      setTimeout(() => setError(''), 3000)
    } catch (err) {
      setError('Failed to copy thread content')
      setTimeout(() => setError(''), 3000)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">GitHub to Blog & Thread Converter</h1>
        
        <div className="bg-black/5 p-8 rounded-lg backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="repo-url" 
                className="block text-sm font-medium text-foreground/70 mb-2"
              >
                GitHub Repository URL
              </label>
              <input
                type="url"
                id="repo-url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="w-full px-4 py-2 bg-background/50 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="https://github.com/username/repository"
                required
                disabled={loading}
              />
            </div>
            
            <button 
              type="submit"
              className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:bg-primary/50"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Generate Blog'}
            </button>
          </form>

          {progress && (
            <div className="mt-4 p-4 bg-primary/10 border border-primary/30 rounded-md text-primary flex items-center justify-center">
              <div className="mr-3 h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
              {progress}
            </div>
          )}

          {error && (
            <div className={`mt-4 p-4 rounded-md ${
              error.includes('copied to clipboard')
                ? 'bg-green-500/10 border border-green-500/30 text-green-500'
                : 'bg-destructive/10 border border-destructive/30 text-destructive'
            }`}>
              {error}
            </div>
          )}

          {blog && (
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Generated Blog Post</h2>
                <div className="flex gap-4">
                  <button
                    onClick={handleCopyBlog}
                    disabled={loading}
                    className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 disabled:bg-secondary/50"
                  >
                    Copy Blog
                  </button>
                  <button
                    onClick={handleConvertToThread}
                    disabled={loading}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:bg-primary/50"
                  >
                    Convert to Thread
                  </button>
                </div>
              </div>
              <div className="bg-background/50 p-4 rounded-md whitespace-pre-wrap border border-border">
                {blog}
              </div>
            </div>
          )}

          {thread && (
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Generated Thread</h2>
                <button
                  onClick={handleCopyThread}
                  disabled={loading}
                  className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 disabled:bg-secondary/50"
                >
                  Copy Thread
                </button>
              </div>
              <div className="bg-background/50 p-4 rounded-md whitespace-pre-wrap border border-border">
                {thread}
              </div>
            </div>
          )}

          {!blog && !error && (
            <div className="mt-8 text-sm text-foreground/70">
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
