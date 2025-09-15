import { useRef, useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'

interface FileItem {
  id: number
  file_name: string
}

export default function DocumentManager() {
  const [directories, setDirectories] = useState<string[]>([])
  const [selectedDir, setSelectedDir] = useState<string>('root')
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
    formData.append('parent', selectedDir === 'root' ? '' : selectedDir)
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
      setError('Unable to create a directory with that name.')
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
    formData.append('directory', selectedDir === 'root' ? '' : selectedDir)
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
    <Box display="flex" height="100vh" border={1} borderColor="grey.400">
      <Box width="25%" display="flex" flexDirection="column" borderRight={1} borderColor="grey.300">
        <Box display="flex" justifyContent="space-between" alignItems="center" p={1} borderBottom={1} borderColor="grey.300">
          <Typography variant="subtitle1">Directories</Typography>
          <Button variant="contained" size="small" onClick={openModal}>Add Directory</Button>
        </Box>
        <Box flexGrow={1} overflow="auto" p={1}>
          <List>
            <ListItemButton
              selected={selectedDir === 'root'}
              onClick={() => setSelectedDir('root')}
            >
              <ListItemText primary="Root" />
            </ListItemButton>
            {directories.map((dir) => (
              <ListItemButton
                key={dir}
                sx={{ pl: 2 }}
                selected={selectedDir === dir}
                onClick={() => setSelectedDir(dir)}
              >
                <ListItemText primary={dir} />
              </ListItemButton>
            ))}
          </List>
        </Box>
        <Box p={1}>
          <Button variant="contained" onClick={triggerUpload}>Upload</Button>
          <input ref={fileInputRef} type="file" hidden onChange={handleUpload} />
        </Box>
      </Box>
      <Box flexGrow={1} display="flex" flexDirection="column">
        <Box p={1} borderBottom={1} borderColor="grey.300">
          <Typography variant="subtitle1">Files</Typography>
        </Box>
        <Box flexGrow={1} overflow="auto" p={1}>
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
        <Box p={1} display="flex" justifyContent="flex-end">
          <Button variant="contained" onClick={handleDownload} disabled={!selectedFile}>Download</Button>
        </Box>
      </Box>
      <Dialog open={showModal} onClose={closeModal} fullWidth maxWidth="xs">
        <DialogTitle>Add New Directory</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="dense"
            value={newDirName}
            onChange={(e) => setNewDirName(e.target.value)}
          />
          {error && (
            <Typography color="error" variant="body2" mt={1}>
              {error}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeModal}>Cancel</Button>
          <Button onClick={handleAddDirectory}>Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
