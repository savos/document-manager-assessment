import { useState } from 'react'
import { TextField, Button, Link } from '@mui/material'
import { useNavigate, Link as RouterLink } from 'react-router-dom'

interface Props {
  onLogin: (token: string) => void
}

export default function SignIn({ onLogin }: Props) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await fetch('/api/accounts/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    if (res.ok) {
      const data = await res.json()
      onLogin(data.token)
      navigate('/documents')
    } else {
      const data = await res.json()
      setError(data.detail || 'Login failed.')
    }
  }

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="space-y-4 rounded bg-white p-8 shadow">
        <h2 className="text-xl font-semibold text-gray-800">Sign In</h2>
        <TextField label="Email" name="email" type="email" fullWidth value={form.email} onChange={handleChange} />
        <TextField
          label="Password"
          name="password"
          type="password"
          fullWidth
          value={form.password}
          onChange={handleChange}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button variant="contained" color="primary" type="submit" fullWidth>
          Login
        </Button>
        <Link component={RouterLink} to="#" underline="hover" className="text-sm">
          Forgot password?
        </Link>
      </form>
    </div>
  )
}
