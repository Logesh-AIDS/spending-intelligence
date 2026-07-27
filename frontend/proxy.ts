import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Auth is handled client-side via AuthGuard (token lives in localStorage, not cookies)
// This proxy does nothing — it just passes every request through
export function proxy(request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [],  // match nothing
};
