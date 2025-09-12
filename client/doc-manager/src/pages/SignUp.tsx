import { useState } from 'react'
import { TextField, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'

const passwordRequirements =
  'Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers.'

const isStrongPassword = (password: string) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(password)

export default function SignUp() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', name: '', password: '', passwordConfirm: '' })
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isStrongPassword(form.password)) {
      setError('Password is too weak.')
      return
    }
    if (form.password !== form.passwordConfirm) {
      setError('Passwords do not match.')
      return
    }
    const res = await fetch('/api/accounts/signup/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: form.email,
        name: form.name,
        password: form.password,
        password_confirm: form.passwordConfirm,
      }),
    })
    if (res.ok) {
      navigate('/signin')
    } else {
      const data = await res.json()
      setError(data.detail || 'Registration failed.')
    }
  }

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="space-y-4 rounded bg-white p-8 shadow">
        <h2 className="text-xl font-semibold text-gray-800">Sign Up</h2>
        <TextField label="Email" name="email" type="email" fullWidth value={form.email} onChange={handleChange} />
        <TextField label="Name" name="name" fullWidth value={form.name} onChange={handleChange} />
        <TextField label="Password" name="password" type="password" fullWidth value={form.password} onChange={handleChange} />
        <p className="text-xs text-gray-600">{passwordRequirements}</p>
        {form.password && !isStrongPassword(form.password) && (
          <p className="text-xs text-red-600">Password is too weak.</p>
        )}
        <TextField
          label="Repeat Password"
          name="passwordConfirm"
          type="password"
          fullWidth
          value={form.passwordConfirm}
          onChange={handleChange}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button
          variant="contained"
          color="primary"
          type="submit"
          fullWidth
          disabled={!isStrongPassword(form.password)}
        >
          Register
        </Button>
      </form>
    </div>
  )
}
