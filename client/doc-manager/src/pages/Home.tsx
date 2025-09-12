import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="flex h-screen flex-col items-center justify-center bg-blue-50">
      <h1 className="mb-8 text-3xl font-bold text-blue-800">Propylon Document Assessment</h1>
      <div className="space-x-4">
        <Link className="text-blue-600 underline" to="/signin">
          Sign In
        </Link>
        <Link className="text-blue-600 underline" to="/signup">
          Sign Up
        </Link>
      </div>
    </div>
  )
}
