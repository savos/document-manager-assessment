import { useRef, useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'

interface FileItem {
  id: number
  file_name: string
}

export default function DocumentManager() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const token = localStorage.getItem('token')
  const authHeader = token ? { Authorization: `Token ${token}` } : {}

  const triggerUpload = () => {
    fileInputRef.current?.click()
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return
    const file = e.target.files[0]
    const formData = new FormData()
    formData.append('file', file)
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
    <Box display="flex" flexDirection="column" height="100vh" m={2}>
      <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Button variant="contained" onClick={triggerUpload}>Upload</Button>
          <input ref={fileInputRef} type="file" hidden onChange={handleUpload} />
        </Box>
        <Button variant="contained" onClick={handleDownload} disabled={!selectedFile}>Download</Button>
      </Box>
      <Box flexGrow={1} display="flex" flexDirection="column">
        <Box mb={2}>
          <Typography variant="subtitle1">Files</Typography>
        </Box>
        <Box flexGrow={1} overflow="auto" sx={{ width: '128ch' }}>
          <List>
            {files.map((file) => (
              <ListItemButton
                key={file.id}
                selected={selectedFile?.id === file.id}
                onClick={() => setSelectedFile(file)}
              >
                <ListItemText primary={file.file_name} />
              </ListItemButton>
            ))}
          </List>
        </Box>
      </Box>
    </Box>
  )
}
