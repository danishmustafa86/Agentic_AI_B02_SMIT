'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface StudentResult {
  name: string;
  rollNo: string;
  score: number;
  percentage: number;
  submittedAt: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [results, setResults] = useState<StudentResult[]>([]);
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordChangeError, setPasswordChangeError] = useState('');
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState('');
  const [adminPassword, setAdminPassword] = useState('DanisHMustafA');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const saved = typeof window !== 'undefined' ? localStorage.getItem('adminPassword') : null;
    if (saved) setAdminPassword(saved);
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === adminPassword) {
      setIsAuthenticated(true);
      setError('');
      fetchResults();
    } else {
      setError('Invalid password');
    }
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordChangeError('');
    setPasswordChangeSuccess('');

    if (!newPassword || !confirmPassword) {
      setPasswordChangeError('Both fields are required');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordChangeError('Passwords do not match');
      return;
    }
    if (newPassword.length < 6) {
      setPasswordChangeError('Password must be at least 6 characters');
      return;
    }

    localStorage.setItem('adminPassword', newPassword);
    setAdminPassword(newPassword);
    setNewPassword('');
    setConfirmPassword('');
    setShowChangePassword(false);
    setPasswordChangeSuccess('Password changed successfully!');
    setTimeout(() => setPasswordChangeSuccess(''), 3000);
  };

  const handleDeleteRecord = async (rollNo: string, name: string) => {
    try {
      setDeleting(true);
      const response = await fetch('/api/delete-result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rollNo }),
      });

      if (response.ok) {
        setDeleteConfirm(null);
        fetchResults();
      } else {
        alert('Failed to delete record');
      }
    } catch (err) {
      console.error('Error deleting record:', err);
      alert('Error deleting record');
    } finally {
      setDeleting(false);
    }
  };

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/get-results');
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error('Failed to fetch results:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch('/api/export-excel');
      if (!response.ok) throw new Error('Export failed');

      const contentType = response.headers.get('content-type');
      const blob = new Blob([await response.arrayBuffer()], {
        type: contentType || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `quiz-results-${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to export:', err);
      alert('Failed to export results');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Admin Login</h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError('');
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter admin password"
              />
            </div>
            {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-shadow"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
            <p className="text-gray-600">Quiz Results & Analytics</p>
          </div>
          <button
            onClick={() => {
              setIsAuthenticated(false);
              setPassword('');
            }}
            className="bg-red-500 text-white px-6 py-2 rounded-lg hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-800">
                Total Students: <span className="text-blue-600">{results.length}</span>
              </h2>
              {results.length > 0 && (
                <p className="text-gray-600 mt-2">
                  Average Score:{' '}
                  <span className="font-semibold">
                    {(results.reduce((acc, r) => acc + r.percentage, 0) / results.length).toFixed(2)}%
                  </span>
                </p>
              )}
            </div>
            <div className="space-x-4">
              <button
                onClick={fetchResults}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                Refresh
              </button>
              <button
                onClick={handleExport}
                disabled={results.length === 0}
                className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📊 Export to Excel
              </button>
              <button
                onClick={() => setShowChangePassword(!showChangePassword)}
                className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors"
              >
                🔐 Change Password
              </button>
            </div>
          </div>

          {/* Change Password Section */}
          {showChangePassword && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Change Admin Password</h3>
              <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      setPasswordChangeError('');
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter new password"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      setPasswordChangeError('');
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Confirm new password"
                  />
                </div>
                {passwordChangeError && (
                  <div className="text-red-500 text-sm font-medium">{passwordChangeError}</div>
                )}
                {passwordChangeSuccess && (
                  <div className="text-green-500 text-sm font-medium">{passwordChangeSuccess}</div>
                )}
                <div className="space-x-4">
                  <button
                    type="submit"
                    className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors"
                  >
                    Update Password
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowChangePassword(false);
                      setNewPassword('');
                      setConfirmPassword('');
                      setPasswordChangeError('');
                    }}
                    className="bg-gray-400 text-white px-6 py-2 rounded-lg hover:bg-gray-500 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Results Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-600">Loading results...</div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              No quiz results yet. Students will appear here after submitting.
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-100 border-b border-gray-300">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Roll No</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Score</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Percentage</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Grade</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Submitted At</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                {results
                  .sort((a, b) => b.percentage - a.percentage)
                  .map((result, index) => {
                    let grade = 'F';
                    if (result.percentage >= 90) grade = 'A';
                    else if (result.percentage >= 80) grade = 'B';
                    else if (result.percentage >= 70) grade = 'C';
                    else if (result.percentage >= 60) grade = 'D';

                    let gradeColor = 'text-red-600';
                    if (grade === 'A') gradeColor = 'text-green-600';
                    else if (grade === 'B') gradeColor = 'text-blue-600';
                    else if (grade === 'C') gradeColor = 'text-yellow-600';
                    else if (grade === 'D') gradeColor = 'text-orange-600';

                    return (
                      <tr
                        key={index}
                        className={`border-b border-gray-200 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                      >
                        <td className="px-6 py-3 text-sm text-gray-800">{result.rollNo}</td>
                        <td className="px-6 py-3 text-sm text-gray-800">{result.name}</td>
                        <td className="px-6 py-3 text-sm font-semibold text-gray-800">{result.score}/50</td>
                        <td className="px-6 py-3 text-sm font-semibold text-gray-800">{result.percentage}%</td>
                        <td className={`px-6 py-3 text-sm font-bold ${gradeColor}`}>{grade}</td>
                        <td className="px-6 py-3 text-sm text-gray-600">
                          {new Date(result.submittedAt).toLocaleString()}
                        </td>
                        <td className="px-6 py-3 text-sm">
                          <button
                            onClick={() => setDeleteConfirm(result.rollNo)}
                            className="text-red-600 hover:text-red-800 font-semibold hover:underline"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-2xl p-6 w-full max-w-sm">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Delete Record</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete the record for student <span className="font-semibold">{results.find(r => r.rollNo === deleteConfirm)?.name}</span> (Roll No: <span className="font-semibold">{deleteConfirm}</span>)? This action cannot be undone.
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={() => handleDeleteRecord(deleteConfirm, results.find(r => r.rollNo === deleteConfirm)?.name || '')}
                  disabled={deleting}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-semibold disabled:opacity-50"
                >
                  {deleting ? 'Deleting...' : 'Delete'}
                </button>
                <button
                  onClick={() => setDeleteConfirm(null)}
                  disabled={deleting}
                  className="flex-1 bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500 transition-colors font-semibold disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
