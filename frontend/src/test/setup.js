import '@testing-library/jest-dom'

// Evitar erros de "Not implemented: HTMLFormElement.prototype.submit" em alguns ambientes
beforeEach(() => {
  if (typeof window !== 'undefined') {
    window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener: () => {}, removeListener: () => {} }))
  }
})
