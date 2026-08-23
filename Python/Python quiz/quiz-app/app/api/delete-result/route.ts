import { NextRequest, NextResponse } from 'next/server';
import { deleteQuizResult, initializeDatabase } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { rollNo } = body;

    if (!rollNo) {
      return NextResponse.json({ error: 'rollNo is required' }, { status: 400 });
    }

    await initializeDatabase();
    await deleteQuizResult(rollNo);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting quiz result:', error);
    return NextResponse.json({ error: 'Failed to delete result' }, { status: 500 });
  }
}
