'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { questions } from '@/lib/questions';

interface ResultData {
  name: string;
  rollNo: string;
  score: number;
  percentage: number;
  answers: Record<number, number>;
  correctAnswers: Record<number, number>;
}

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<ResultData | null>(null);
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    const data = sessionStorage.getItem('quizResult');
    if (!data) {
      router.push('/');
      return;
    }
    setResult(JSON.parse(data));
  }, [router]);

  if (!result) {
    return <div className="text-center mt-10">Loading results...</div>;
  }

  const getGrade = (percentage: number) => {
    if (percentage >= 90) return { grade: 'A', color: 'text-green-600' };
    if (percentage >= 80) return { grade: 'B', color: 'text-blue-600' };
    if (percentage >= 70) return { grade: 'C', color: 'text-yellow-600' };
    if (percentage >= 60) return { grade: 'D', color: 'text-orange-600' };
    return { grade: 'F', color: 'text-red-600' };
  };

  const gradeInfo = getGrade(result.percentage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Result Card */}
        <div className="bg-white rounded-lg shadow-2xl p-8 mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Quiz Completed!</h1>
          <p className="text-gray-600 mb-8">
            {result.name} (Roll: {result.rollNo})
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <p className="text-gray-600 text-sm mb-2">Score</p>
              <p className="text-4xl font-bold text-blue-600">
                {result.score}/{questions.length}
              </p>
            </div>

            <div className="bg-purple-50 p-6 rounded-lg">
              <p className="text-gray-600 text-sm mb-2">Percentage</p>
              <p className="text-4xl font-bold text-purple-600">{result.percentage}%</p>
            </div>

            <div className={`bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-lg`}>
              <p className="text-gray-600 text-sm mb-2">Grade</p>
              <p className={`text-4xl font-bold ${gradeInfo.color}`}>{gradeInfo.grade}</p>
            </div>
          </div>

          <div className="text-gray-600 mb-8">
            <p className="text-lg">
              ✓ Correct: <span className="font-semibold text-green-600">{result.score}</span>
            </p>
            <p className="text-lg">
              ✗ Incorrect: <span className="font-semibold text-red-600">{questions.length - result.score}</span>
            </p>
          </div>

          <button
            onClick={() => setShowAnswers(!showAnswers)}
            className="mb-6 bg-indigo-600 text-white py-2 px-8 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {showAnswers ? 'Hide Answer Key' : 'View Answer Key'}
          </button>
        </div>

        {/* Answer Key */}
        {showAnswers && (
          <div className="space-y-4 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Answer Key</h2>
            {questions.map((question, index) => {
              const userAnswer = result.answers[question.id];
              const isCorrect = userAnswer === result.correctAnswers[question.id];

              return (
                <div key={question.id} className={`p-6 rounded-lg ${isCorrect ? 'bg-green-50 border-l-4 border-green-500' : 'bg-red-50 border-l-4 border-red-500'}`}>
                  <h4 className="font-semibold text-gray-800 mb-3">
                    Q{index + 1}: {question.question}
                  </h4>
                  <div className="space-y-2">
                    {question.options.map((option, optIdx) => {
                      const isUserChoice = userAnswer === optIdx;
                      const isCorrectChoice = result.correctAnswers[question.id] === optIdx;

                      return (
                        <div
                          key={optIdx}
                          className={`p-2 rounded ${
                            isCorrectChoice
                              ? 'bg-green-200 text-green-900'
                              : isUserChoice
                              ? 'bg-red-200 text-red-900'
                              : 'text-gray-700'
                          }`}
                        >
                          {isCorrectChoice && <span className="font-bold">✓ </span>}
                          {isUserChoice && !isCorrectChoice && <span className="font-bold">✗ </span>}
                          {option}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Exit Button */}
        <div className="text-center">
          <button
            onClick={() => {
              sessionStorage.removeItem('studentData');
              sessionStorage.removeItem('quizResult');
              router.push('/');
            }}
            className="bg-gray-600 text-white py-3 px-8 rounded-lg hover:bg-gray-700 transition-colors font-semibold"
          >
            Exit to Home
          </button>
        </div>
      </div>
    </div>
  );
}
