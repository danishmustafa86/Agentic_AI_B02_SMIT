import { NextResponse } from 'next/server';
import * as XLSX from 'xlsx';
import { getAllQuizResults, initializeDatabase } from '@/lib/db';

export async function GET() {
  try {
    await initializeDatabase();
    const results = await getAllQuizResults();

    // Prepare data for Excel
    const worksheetData = [
      ['Roll No', 'Name', 'Score', 'Percentage', 'Grade', 'Submitted At'],
      ...results
        .sort((a: any, b: any) => b.percentage - a.percentage)
        .map((result: any) => {
          let grade = 'F';
          if (result.percentage >= 90) grade = 'A';
          else if (result.percentage >= 80) grade = 'B';
          else if (result.percentage >= 70) grade = 'C';
          else if (result.percentage >= 60) grade = 'D';

          return [
            result.rollNo,
            result.name,
            `${result.score}/50`,
            `${result.percentage}%`,
            grade,
            new Date(result.submittedAt).toLocaleString(),
          ];
        }),
      // Summary row
      ['', '', '', '', '', ''],
      ['SUMMARY', '', '', '', '', ''],
      [
        'Total Students:',
        results.length,
        '',
        '',
        '',
        '',
      ],
      [
        'Average Percentage:',
        results.length > 0
          ? (
              results.reduce((acc: number, r: any) => acc + r.percentage, 0) /
              results.length
            ).toFixed(2) + '%'
          : 'N/A',
        '',
        '',
        '',
        '',
      ],
      [
        'Highest Score:',
        results.length > 0
          ? Math.max(...results.map((r: any) => r.percentage)) + '%'
          : 'N/A',
        '',
        '',
        '',
        '',
      ],
      [
        'Lowest Score:',
        results.length > 0
          ? Math.min(...results.map((r: any) => r.percentage)) + '%'
          : 'N/A',
        '',
        '',
        '',
        '',
      ],
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Results');

    // Style the header row
    worksheet['!cols'] = [
      { wch: 12 },
      { wch: 20 },
      { wch: 12 },
      { wch: 12 },
      { wch: 8 },
      { wch: 20 },
    ];

    const buffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });

    return new NextResponse(Buffer.from(buffer), {
      status: 200,
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': `attachment; filename="quiz-results-${new Date().toISOString().split('T')[0]}.xlsx"`,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Length': Buffer.from(buffer).length.toString(),
      },
    });
  } catch (error) {
    console.error('Error exporting Excel:', error);
    return NextResponse.json({ error: 'Failed to export' }, { status: 500 });
  }
}
