'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface StudentResult {
  id: number;
  name: string;
  score: number;
  percentage: number;
  submittedAt: string;
}

export default function Home() {
  const [name, setName] = useState('');
  const [rollNo, setRollNo] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [previousResult, setPreviousResult] = useState<StudentResult | null>(null);
  const router = useRouter();

  const checkStudentStatus = async (studentRollNo: string) => {
    try {
      setLoading(true);
      const response = await fetch('/api/check-student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rollNo: studentRollNo }),
      });

      const data = await response.json();

      if (data.hasAttempted) {
        setPreviousResult(data.result);
        setError('');
        return false; // Already taken
      }

      setPreviousResult(null);
      return true; // Can take exam
    } catch (err) {
      console.error('Error checking student:', err);
      setError('Failed to check student status');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!rollNo.trim()) {
      setError('Please enter your roll number');
      return;
    }

    const canTakeExam = await checkStudentStatus(rollNo.trim());

    if (!canTakeExam) {
      return; // Show previous result instead
    }

    const studentData = {
      name: name.trim(),
      rollNo: rollNo.trim(),
      startTime: new Date().toISOString(),
    };

    sessionStorage.setItem('studentData', JSON.stringify(studentData));
    router.push('/quiz');
  };

  // Show previous result if student already took exam
  if (previousResult) {
    let grade = 'F';
    if (previousResult.percentage >= 90) grade = 'A';
    else if (previousResult.percentage >= 80) grade = 'B';
    else if (previousResult.percentage >= 70) grade = 'C';
    else if (previousResult.percentage >= 60) grade = 'D';

    let gradeColor = 'text-red-600';
    if (grade === 'A') gradeColor = 'text-green-600';
    else if (grade === 'B') gradeColor = 'text-blue-600';
    else if (grade === 'C') gradeColor = 'text-yellow-600';
    else if (grade === 'D') gradeColor = 'text-orange-600';

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md text-center">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Python Quiz</h1>
            <p className="text-gray-600">Results</p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
            <p className="text-gray-700 mb-2">
              <span className="font-semibold">Student:</span> {previousResult.name}
            </p>
            <p className="text-gray-700 mb-4">
              <span className="font-semibold">Roll No:</span> {rollNo}
            </p>

            <div className="bg-white rounded-lg p-4 mb-4">
              <p className="text-5xl font-bold text-blue-600 mb-2">
                {previousResult.score}/50
              </p>
              <p className="text-2xl font-bold mb-2">
                {previousResult.percentage}%
              </p>
              <p className={`text-3xl font-bold ${gradeColor}`}>
                Grade: {grade}
              </p>
            </div>

            <p className="text-sm text-gray-600">
              Submitted on: {new Date(previousResult.submittedAt).toLocaleString()}
            </p>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-800 font-semibold">
              ⚠️ You have already taken this exam
            </p>
            <p className="text-yellow-700 text-sm mt-2">
              Each student can attempt the quiz only once. Your results above are your final score.
            </p>
          </div>

          <button
            onClick={() => {
              setName('');
              setRollNo('');
              setPreviousResult(null);
              setError('');
            }}
            className="w-full bg-gradient-to-r from-gray-600 to-gray-700 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-shadow"
          >
            Check Another Student
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Python Quiz</h1>
          <p className="text-gray-600">Medium Level Assessment</p>
        </div>

        <form onSubmit={handleStart} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setError('');
                setPreviousResult(null);
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your full name"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Roll Number *
            </label>
            <input
              type="text"
              value={rollNo}
              onChange={(e) => {
                setRollNo(e.target.value);
                setError('');
                setPreviousResult(null);
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your roll number"
              disabled={loading}
            />
          </div>

          {error && <div className="text-red-500 text-sm font-medium">{error}</div>}

          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Duration:</span> 40 minutes<br/>
              <span className="font-semibold">Questions:</span> 50 MCQs<br/>
              <span className="font-semibold">Level:</span> Medium
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Checking...' : 'Start Quiz'}
          </button>
        </form>

        <p className="text-xs text-gray-500 text-center mt-6">
          Please ensure you have at least 40 minutes available before starting.
        </p>
      </div>
    </div>
  );
}
