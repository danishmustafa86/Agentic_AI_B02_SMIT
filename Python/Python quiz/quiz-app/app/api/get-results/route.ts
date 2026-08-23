import { NextResponse } from 'next/server';
import { getAllQuizResults, initializeDatabase } from '@/lib/db';

export async function GET() {
  try {
    console.log('GET /api/get-results called');
    console.log('POSTGRES_URL exists:', !!process.env.POSTGRES_URL);

    await initializeDatabase();
    const results = await getAllQuizResults();

    console.log('Results fetched:', results.length);
    return NextResponse.json({ results });
  } catch (error) {
    console.error('Error fetching results:', error);
    return NextResponse.json({ error: 'Failed to fetch results', details: String(error) }, { status: 500 });
  }
}
