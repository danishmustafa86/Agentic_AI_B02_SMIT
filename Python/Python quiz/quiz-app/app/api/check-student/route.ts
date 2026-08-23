import { NextRequest, NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';
import { initializeDatabase } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    await initializeDatabase();
    const body = await request.json();
    const { rollNo } = body;

    if (!rollNo) {
      return NextResponse.json({ error: 'Roll number required' }, { status: 400 });
    }

    console.log(`Checking if student ${rollNo} has taken exam...`);

    const result = await sql`
      SELECT id, name, score, percentage, submitted_at as "submittedAt"
      FROM quiz_results
      WHERE roll_no = ${rollNo}
      LIMIT 1
    `;

    if (result.rows.length > 0) {
      const studentResult = result.rows[0];
      console.log(`✓ Student ${rollNo} has already taken exam`);
      return NextResponse.json({
        hasAttempted: true,
        result: studentResult,
      });
    }

    console.log(`✓ Student ${rollNo} can take exam`);
    return NextResponse.json({ hasAttempted: false });
  } catch (error) {
    console.error('❌ Error checking student:', error);
    return NextResponse.json({ error: 'Failed to check student status' }, { status: 500 });
  }
}
