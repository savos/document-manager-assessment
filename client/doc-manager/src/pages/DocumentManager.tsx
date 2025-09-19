import { useCallback, useEffect, useState } from 'react'
import type { MouseEvent } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Typography from '@mui/material/Typography'
import Link from '@mui/material/Link'
import { useNavigate } from 'react-router-dom'

interface UserFileResponseItem {
  id?: number
  file_name: string
  version: number
  digest_hex?: string | null
}

interface AllFilesResponseItem {
  id: number
  file_name: string
  version_number: number
  digest_hex: string | null
}

type FileView = 'user' | 'all'

interface FileItem {
  id?: number
  file_name: string
  version?: number
  digest_hex?: string | null
}

const areSameFile = (first: FileItem | null, second: FileItem | null) => {
  if (!first || !second) {
    return false
  }

  if (first.id != null && second.id != null) {
    return first.id === second.id
  }

  return (
    first.file_name === second.file_name &&
    (first.version ?? null) === (second.version ?? null) &&
    (first.digest_hex ?? null) === (second.digest_hex ?? null)
  )
}

export default function DocumentManager() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [activeView, setActiveView] = useState<FileView>('user')
  const navigate = useNavigate()
  const token = localStorage.getItem('token')
  const authHeader = token ? { Authorization: `Token ${token}` } : undefined

  const fetchFiles = useCallback(
    async (endpoint: string, targetView: FileView) => {
      setActiveView(targetView)

      try {
        const response = await fetch(endpoint, {
          ...(token ? { headers: { Authorization: `Token ${token}` } } : {}),
        })

        if (!response.ok) {
          setFiles([])
          setSelectedFile(null)
          return
        }

        const rawData = await response.json()

        const normalisedData: FileItem[] =
          targetView === 'all'
            ? (rawData as AllFilesResponseItem[]).map((item) => ({
                id: item.id,
                file_name: item.file_name,
                version: item.version_number,
                digest_hex: item.digest_hex ?? null,
              }))
            : (rawData as UserFileResponseItem[]).map((item) => ({
                id: item.id,
                file_name: item.file_name,
                version: item.version,
                digest_hex: item.digest_hex ?? null,
              }))

        setFiles(normalisedData)
        setSelectedFile((previous) => {
          if (!previous) {
            return null
          }

          const updatedSelection = normalisedData.find((file) => areSameFile(file, previous))
          return updatedSelection ?? null
        })
      } catch (error) {
        console.error('Unable to load files.', error)
        setFiles([])
        setSelectedFile(null)
      }
    },
    [token],
  )

  useEffect(() => {
    fetchFiles('/api/files/user/', 'user')
  }, [fetchFiles])

  const handleShowUserFiles = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault()
    fetchFiles('/api/files/user/', 'user')
  }

  const handleShowAllFiles = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault()
    fetchFiles('/api/files/', 'all')
  }

  const handleDiff = () => {}

  const handleSignOut = () => {
    localStorage.removeItem('token')
    navigate('/')
  }

  const handleDownload = async () => {
    if (!selectedFile?.id) return
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
      <Box display="flex" flexDirection="column" flexGrow={1} pb={9} sx={{ width: '64ch' }}>
        <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
          <Button variant="contained">Upload</Button>
          <Button variant="contained" onClick={handleDownload} disabled={!selectedFile?.id}>
            Download
          </Button>
        </Box>
        <Box flexGrow={1} display="flex" flexDirection="column">
          <Box mb={2} display="flex" justifyContent="space-between" alignItems="center">
            <Link href="#" underline="hover" onClick={handleShowUserFiles}>
              Files
            </Link>
            <Link href="#" underline="hover" onClick={handleShowAllFiles}>
              All Files
            </Link>
          </Box>
          <Box
            flexGrow={1}
            overflow="auto"
            sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1 }}
          >
            <List>
              {files.map((file) => (
                <ListItemButton
                  key={
                    file.id ??
                    `${file.file_name}-${file.version ?? 'unknown'}-${file.digest_hex ?? 'none'}`
                  }
                  selected={areSameFile(file, selectedFile)}
                  onClick={() => setSelectedFile(file)}
                >
                  <ListItemText
                    primary={file.file_name}
                    secondary={
                      activeView === 'all'
                        ? `Version ${file.version ?? 'Unknown'} • Digest ${
                            file.digest_hex ?? 'Unavailable'
                          }`
                        : file.version != null
                        ? `Version ${file.version}`
                        : undefined
                    }
                  />
                </ListItemButton>
              ))}
            </List>
          </Box>
          <Box mt={2} display="flex" justifyContent="center">
            <Button variant="contained" onClick={handleDiff}>
              Diff
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}
