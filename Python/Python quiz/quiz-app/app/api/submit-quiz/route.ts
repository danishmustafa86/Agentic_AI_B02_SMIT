import { NextRequest, NextResponse } from 'next/server';
import { saveQuizResult, initializeDatabase } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    console.log('POST /api/submit-quiz called');
    console.log('POSTGRES_URL exists:', !!process.env.POSTGRES_URL);

    await initializeDatabase();
    const body = await request.json();

    console.log('Saving result for:', body.name, body.rollNo);

    await saveQuizResult({
      name: body.name,
      rollNo: body.rollNo,
      score: body.score,
      percentage: body.percentage,
      submittedAt: body.submittedAt,
    });

    console.log('Result saved successfully');
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error saving quiz result:', error);
    return NextResponse.json({ error: 'Failed to save result', details: String(error) }, { status: 500 });
  }
}
