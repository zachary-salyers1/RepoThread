'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('')
  const [blog, setBlog] = useState('')
  const [thread, setThread] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [currentJobId, setCurrentJobId] = useState('')
  const [progress, setProgress] = useState<string>('')

  const pollJobStatus = async (jobId: string, type: 'analyze' | 'convert') => {
    try {
      const endpoint = type === 'analyze' ? '/api/analyze' : '/api/convert-thread'
      const response = await fetch(`${endpoint}?jobId=${jobId}`)
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
        setCurrentJobId('')
        return true
      } else if (data.status === 'pending') {
        // Update progress message
        setProgress(type === 'analyze' ? 'Analyzing repository...' : 'Converting to thread...')
        // Continue polling
        setTimeout(() => pollJobStatus(jobId, type), 5000)
        return false
      } else {
        throw new Error('Job failed: ' + data.result)
      }
    } catch (error) {
      setLoading(false)
      setProgress('')
      setError(error instanceof Error ? error.message : String(error))
      setCurrentJobId('')
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

      setCurrentJobId(data.job_id)
      pollJobStatus(data.job_id, 'analyze')
    } catch (error) {
      setLoading(false)
      setProgress('')
      setError(error instanceof Error ? error.message : String(error))
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

      setCurrentJobId(data.job_id)
      pollJobStatus(data.job_id, 'convert')
    } catch (error) {
      setLoading(false)
      setProgress('')
      setError(error instanceof Error ? error.message : String(error))
    }
  }

  const handleCopyBlog = async () => {
    try {
      await navigator.clipboard.writeText(blog)
      setError('Blog content copied to clipboard!')
      setTimeout(() => setError(''), 3000)
    } catch (error) {
      setError('Failed to copy blog content')
    }
  }

  const handleCopyThread = async () => {
    try {
      await navigator.clipboard.writeText(thread)
      setError('Thread content copied to clipboard!')
      setTimeout(() => setError(''), 3000)
    } catch (error) {
      setError('Failed to copy thread content')
    }
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">GitHub to Blog to Thread</h1>
      
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Enter GitHub repository URL"
            className="flex-1 p-2 border rounded"
            required
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? 'Processing...' : 'Generate Blog'}
          </button>
        </div>
      </form>

      {progress && (
        <div className="mb-8 p-4 bg-blue-100 text-blue-700 rounded flex items-center justify-center">
          <div className="mr-3 h-4 w-4 animate-spin rounded-full border-2 border-blue-700 border-t-transparent"></div>
          {progress}
        </div>
      )}

      {error && (
        <div className={`mb-8 p-4 rounded ${
          error.includes('copied to clipboard') 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        }`}>
          {error}
        </div>
      )}

      {blog && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Generated Blog Post</h2>
            <div className="flex gap-4">
              <button
                onClick={handleCopyBlog}
                disabled={loading}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:bg-gray-400"
              >
                Copy Blog
              </button>
              <button
                onClick={handleConvertToThread}
                disabled={loading}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
              >
                Convert to Thread
              </button>
            </div>
          </div>
          <div className="p-4 bg-gray-100 rounded whitespace-pre-wrap">
            {blog}
          </div>
        </div>
      )}

      {thread && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Generated Thread</h2>
            <button
              onClick={handleCopyThread}
              disabled={loading}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:bg-gray-400"
            >
              Copy Thread
            </button>
          </div>
          <div className="p-4 bg-gray-100 rounded whitespace-pre-wrap">
            {thread}
          </div>
        </div>
      )}
    </main>
  )
}
