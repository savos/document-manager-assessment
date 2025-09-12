import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import SignUp from './SignUp'

describe('SignUp', () => {
  it('disables registration until password is strong', () => {
    render(
      <MemoryRouter>
        <SignUp />
      </MemoryRouter>,
    )
    const passwordInput = screen.getByLabelText('Password')
    const confirmInput = screen.getByLabelText('Repeat Password')
    const registerButton = screen.getByRole('button', { name: /register/i })

    expect(registerButton).toBeDisabled()

    fireEvent.change(passwordInput, { target: { value: 'weak' } })
    fireEvent.change(confirmInput, { target: { value: 'weak' } })
    expect(registerButton).toBeDisabled()

    fireEvent.change(passwordInput, { target: { value: 'Str0ngPass' } })
    fireEvent.change(confirmInput, { target: { value: 'Str0ngPass' } })
    expect(registerButton).not.toBeDisabled()
  })
})
