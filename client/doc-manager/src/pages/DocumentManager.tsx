import { useRef, useState } from 'react'

interface FileItem {
  id: number
  file_name: string
}

export default function DocumentManager() {
  const [directories, setDirectories] = useState<string[]>([])
  const [selectedDir, setSelectedDir] = useState<string>('')
  const [files, setFiles] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [newDirName, setNewDirName] = useState('')
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const token = localStorage.getItem('token')
  const authHeader = token ? { Authorization: `Token ${token}` } : {}

  const openModal = () => {
    setNewDirName('')
    setError('')
    setShowModal(true)
  }

  const closeModal = () => setShowModal(false)

  const handleAddDirectory = async () => {
    if (!newDirName) {
      return
    }
    const formData = new FormData()
    formData.append('parent', selectedDir)
    formData.append('name', newDirName)
    const response = await fetch('/api/file_versions/directories/', {
      method: 'POST',
      headers: authHeader,
      body: formData,
    })
    if (response.ok) {
      setDirectories([...directories, newDirName])
      closeModal()
    } else {
      setError('Unable to create directory with that name.')
    }
  }

  const triggerUpload = () => {
    fileInputRef.current?.click()
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return
    const file = e.target.files[0]
    const formData = new FormData()
    formData.append('file', file)
    formData.append('directory', selectedDir)
    const response = await fetch('/api/file_versions/upload/', {
      method: 'POST',
      headers: authHeader,
      body: formData,
    })
    if (response.ok) {
      const data = await response.json()
      setFiles([...files, data])
    }
    e.target.value = ''
  }

  const handleDownload = async () => {
    if (!selectedFile) return
    const response = await fetch(`/api/file_versions/${selectedFile.id}/download/`, {
      headers: authHeader,
    })
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = selectedFile.file_name
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    }
  }

  return (
    <div className="flex h-screen border border-gray-400">
      <div className="w-1/4 flex h-full flex-col border border-gray-300">
        <div className="flex items-center justify-between border-b p-2">
          <span className="font-semibold">Tree</span>
          <button onClick={openModal} className="rounded bg-blue-600 px-2 py-1 text-white">New Folder</button>
        </div>
        <div className="flex-1 overflow-auto">
          <ul className="p-2">
            <li
              className={`cursor-pointer p-1 ${selectedDir === '' ? 'font-bold' : ''}`}
              onClick={() => setSelectedDir('')}
            >
              Root
            </li>
            {directories.map((dir) => (
              <li
                key={dir}
                className={`cursor-pointer p-1 ${selectedDir === dir ? 'font-bold' : ''}`}
                onClick={() => setSelectedDir(dir)}
              >
                {dir}
              </li>
            ))}
          </ul>
        </div>
        <div className="p-2">
          <button onClick={triggerUpload} className="rounded bg-green-600 px-2 py-1 text-white">Upload</button>
          <input ref={fileInputRef} type="file" className="hidden" onChange={handleUpload} />
        </div>
      </div>
      <div className="flex-1 flex h-full flex-col border border-gray-300">
        <div className="flex items-center justify-between border-b p-2">
          <span className="font-semibold">Files</span>
        </div>
        <div className="flex-1 overflow-auto">
          <ul className="p-2">
            {files.map((file) => (
              <li
                key={file.id}
                className={`cursor-pointer p-1 ${selectedFile?.id === file.id ? 'bg-gray-200' : ''}`}
                onClick={() => setSelectedFile(file)}
              >
                {file.file_name}
              </li>
            ))}
          </ul>
        </div>
        <div className="p-2 flex justify-end">
          <button
            onClick={handleDownload}
            disabled={!selectedFile}
            className="rounded bg-blue-600 px-2 py-1 text-white disabled:opacity-50"
          >
            Download
          </button>
        </div>
      </div>
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-80 rounded bg-white p-4">
            <label className="mb-2 block text-sm font-medium">Add New Directory</label>
            <input
              className="mb-4 w-full rounded border p-2"
              value={newDirName}
              onChange={(e) => setNewDirName(e.target.value)}
            />
            {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
            <div className="flex justify-end space-x-2">
              <button onClick={closeModal} className="rounded bg-gray-300 px-3 py-1">Cancel</button>
              <button onClick={handleAddDirectory} className="rounded bg-blue-600 px-3 py-1 text-white">Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
