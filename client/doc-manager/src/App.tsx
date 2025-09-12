import { Route, Routes, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Home from './pages/Home'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import DocumentManager from './pages/DocumentManager'

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }, [token])

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/signin" element={<SignIn onLogin={setToken} />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/documents" element={token ? <DocumentManager /> : <Navigate to="/signin" />} />
    </Routes>
  )
}
