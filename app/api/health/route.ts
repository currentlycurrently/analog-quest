import { NextResponse } from 'next/server';
import { checkConnection, getStats } from '@/lib/db';

export async function GET() {
  const healthy = await checkConnection();
  const stats = healthy ? await getStats() : null;

  return NextResponse.json({
    status: healthy ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    database: healthy ? 'connected' : 'disconnected',
    stats,
  }, { status: healthy ? 200 : 503 });
}
