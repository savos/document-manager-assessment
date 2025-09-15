import { useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'
import Link from '@mui/material/Link'
import { useNavigate } from 'react-router-dom'

interface FileItem {
  id: number
  file_name: string
}

export default function DocumentManager() {
  const [files] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const navigate = useNavigate()
  const token = localStorage.getItem('token')
  const authHeader = token ? { Authorization: `Token ${token}` } : undefined

  const handleSignOut = () => {
    localStorage.removeItem('token')
    navigate('/')
  }

  const handleDownload = async () => {
    if (!selectedFile) return
    const response = await fetch(`/api/file_versions/${selectedFile.id}/download/`, {
      ...(authHeader ? { headers: authHeader } : {}),
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
      <Box
        component="header"
        mb={2}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
      >
        <Typography variant="h6">Document Manager</Typography>
        <Link
          href="#"
          underline="hover"
          onClick={(e) => {
            e.preventDefault()
            handleSignOut()
          }}
        >
          Sign Out
        </Link>
      </Box>
      <Box display="flex" flexDirection="column" flexGrow={1} sx={{ width: '64ch' }}>
        <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
          <Button variant="contained" disabled>
            Upload
          </Button>
          <Button variant="contained" onClick={handleDownload} disabled={!selectedFile}>Download</Button>
        </Box>
        <Box flexGrow={1} display="flex" flexDirection="column">
          <Box mb={2}>
            <Typography variant="subtitle1">Files</Typography>
          </Box>
          <Box flexGrow={1} overflow="auto">
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
          <Box mt={2} display="flex" justifyContent="center">
            <Button variant="outlined">Diff</Button>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}
