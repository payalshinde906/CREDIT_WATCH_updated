export function isValidGstin(value = '') {
  const gstin = value.trim().toUpperCase()
  const pattern = /^[0-9]{2}[A-Z]{5}[0-9A-Z]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/
  return pattern.test(gstin)
}
