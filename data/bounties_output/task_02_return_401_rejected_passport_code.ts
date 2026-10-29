// Fix: Return HTTP 401 for rejected Passport exchange codes
// Distinguishes rejected/unauthorized authorization codes from internal errors.

export function handlePassportCallbackResponse(status: number, body: any): { status: number; error: string } {
  if (status === 401 || body?.error === 'invalid_grant' || body?.error === 'rejected_code') {
    return {
      status: 401,
      error: 'passport_rejected_code'
    };
  }
  if (status >= 500) {
    return {
      status: 502,
      error: 'passport_unavailable'
    };
  }
  return {
    status: 200,
    error: 'none'
  };
}
