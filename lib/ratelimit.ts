/**
 * Rate limiting for Analog Quest API endpoints.
 *
 * Uses Upstash Redis via @upstash/ratelimit. Sliding window algorithm because
 * it's cheap, predictable, and doesn't let burst traffic slip through fixed
 * windows at the boundary.
 *
 * Keyed by user ID (for auth-gated endpoints) or IP (for public reads).
 *
 * Safe no-op fallback: if UPSTASH_REDIS_REST_URL isn't configured, every call
 * returns { success: true }. Lets local dev run without Upstash credentials.
 */

import { NextResponse } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = process.env.UPSTASH_REDIS_REST_URL
  ? new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL,
      token: process.env.UPSTASH_REDIS_REST_TOKEN!,
    })
  : null;

function makeLimiter(key: string, requests: number, window: `${number} ${'s' | 'm' | 'h' | 'd'}`) {
  if (!redis) return null;
  return new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(requests, window),
    analytics: true,
    prefix: `aq:${key}`,
  });
}

// Tuned for the actual expected usage, not worst-case paranoia.
// Numbers chosen based on: (a) what a well-behaved agent needs to make
// reasonable progress, (b) what an abusive client would need to cause harm.
export const limiters = {
  // A contributor reading one paper at a time should never hit this.
  // A script trying to lock the queue would.
  queueNext: makeLimiter('queue:next', 6, '1 m'),
  queueSubmit: makeLimiter('queue:submit', 6, '1 m'),

  // Pipeline mode fetches batches of 10. 10 req/min = 100 papers/min throughput.
  pipelineBatch: makeLimiter('pipeline:batch', 10, '1 m'),
  pipelineSubmit: makeLimiter('pipeline:submit', 60, '1 m'),

  // Public reads — generous but not unlimited. Per IP.
  publicRead: makeLimiter('public:read', 60, '1 m'),

  // Admin endpoints (moderator actions). Generous — moderators should
  // be able to click through 60 reviews in a minute if they're fast.
  adminAction: makeLimiter('admin:action', 120, '1 m'),
} as const;

type LimiterKey = keyof typeof limiters;

/**
 * Apply a rate limit to the current request. Returns either:
 *   - null if allowed (request can proceed)
 *   - a NextResponse with 429 if rejected
 *
 * Usage:
 *   const limited = await rateLimit('queueNext', `user:${userId}`);
 *   if (limited) return limited;
 */
export async function rateLimit(
  key: LimiterKey,
  identifier: string
): Promise<NextResponse | null> {
  const limiter = limiters[key];
  if (!limiter) return null; // Upstash not configured, fail-open

  const { success, limit, remaining, reset } = await limiter.limit(identifier);

  if (success) return null;

  const retryAfterSec = Math.max(1, Math.ceil((reset - Date.now()) / 1000));
  return NextResponse.json(
    {
      error: 'rate limit exceeded',
      limit,
      remaining,
      retry_after_seconds: retryAfterSec,
    },
    {
      status: 429,
      headers: {
        'Retry-After': String(retryAfterSec),
        'X-RateLimit-Limit': String(limit),
        'X-RateLimit-Remaining': String(remaining),
        'X-RateLimit-Reset': String(Math.floor(reset / 1000)),
      },
    }
  );
}
