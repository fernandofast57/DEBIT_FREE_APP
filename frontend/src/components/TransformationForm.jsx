
import React, { useState } from 'react';
import axios from 'axios';

export default function TransformationForm() {
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await axios.post('/api/v1/transformations/transform', {
        euro_amount: parseFloat(amount)
      });
      setSuccess(true);
      setAmount('');
    } catch (err) {
      setError(err.response?.data?.message || 'Error during transformation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">New Transformation</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="amount" className="block text-sm font-medium mb-2">
            Amount (EUR)
          </label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full p-2 border rounded"
            min="0"
            step="0.01"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Transform to Gold'}
        </button>
        {error && <p className="mt-2 text-red-600">{error}</p>}
        {success && (
          <p className="mt-2 text-green-600">
            Transformation completed successfully!
          </p>
        )}
      </form>
    </div>
  );
}
