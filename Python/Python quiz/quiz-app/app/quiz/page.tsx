'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { questions } from '@/lib/questions';
import { formatTime } from '@/lib/utils';

const QUIZ_DURATION = 40 * 60; // 40 minutes in seconds

export default function QuizPage() {
  const router = useRouter();
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [timeLeft, setTimeLeft] = useState(QUIZ_DURATION);
  const [submitted, setSubmitted] = useState(false);
  const [studentData, setStudentData] = useState<any>(null);

  useEffect(() => {
    const data = sessionStorage.getItem('studentData');
    if (!data) {
      router.push('/');
      return;
    }
    setStudentData(JSON.parse(data));
  }, [router]);

  useEffect(() => {
    if (!studentData) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [studentData]);

  const handleAnswerChange = (questionId: number, optionIndex: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmit = async () => {
    if (submitted) return;
    setSubmitted(true);

    const correctAnswers: Record<number, number> = {};
    questions.forEach((q) => {
      correctAnswers[q.id] = q.correctAnswer;
    });

    let score = 0;
    for (let i = 1; i <= questions.length; i++) {
      if (answers[i] === correctAnswers[i]) {
        score++;
      }
    }

    const submissionData = {
      ...studentData,
      answers,
      correctAnswers,
      score,
      percentage: Math.round((score / questions.length) * 100),
      submittedAt: new Date().toISOString(),
    };

    await fetch('/api/submit-quiz', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submissionData),
    });

    sessionStorage.setItem('quizResult', JSON.stringify(submissionData));
    router.push('/results');
  };

  if (!studentData) {
    return <div className="text-center mt-10">Loading...</div>;
  }

  const timeoutWarning = timeLeft < 300; // Less than 5 minutes

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Python Quiz</h1>
            <p className="text-gray-600">
              {studentData.name} (Roll: {studentData.rollNo})
            </p>
          </div>
          <div className={`text-center ${timeoutWarning ? 'bg-red-100' : 'bg-blue-100'} p-4 rounded-lg`}>
            <p className="text-sm text-gray-600">Time Left</p>
            <p className={`text-3xl font-bold ${timeoutWarning ? 'text-red-600' : 'text-blue-600'}`}>
              {formatTime(timeLeft)}
            </p>
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-6 mb-8">
          {questions.map((question, index) => (
            <div key={question.id} className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Q{index + 1}: {question.question}
              </h3>
              <div className="space-y-3">
                {question.options.map((option, optionIndex) => (
                  <label key={optionIndex} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-blue-50 transition">
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={optionIndex}
                      checked={answers[question.id] === optionIndex}
                      onChange={() => handleAnswerChange(question.id, optionIndex)}
                      className="mr-3"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={submitted}
            className="bg-gradient-to-r from-green-500 to-green-600 text-white font-bold py-3 px-12 rounded-lg hover:shadow-lg transition-shadow disabled:opacity-50"
          >
            {submitted ? 'Submitting...' : 'Submit Quiz'}
          </button>
        </div>
      </div>
    </div>
  );
}
