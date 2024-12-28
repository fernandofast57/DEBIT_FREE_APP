
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function TransactionList() {
  const [transactions, setTransactions] = useState([]);
  
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await axios.get('/api/v1/transformations/history');
        setTransactions(response.data);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    };
    
    fetchTransactions();
    const interval = setInterval(fetchTransactions, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-bold mb-4">Transazioni Recenti</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="px-4 py-2">Data</th>
              <th className="px-4 py-2">Euro</th>
              <th className="px-4 py-2">Grammi Oro</th>
              <th className="px-4 py-2">Stato</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, index) => (
              <tr key={index} className="border-t">
                <td className="px-4 py-2">{new Date(tx.timestamp).toLocaleString()}</td>
                <td className="px-4 py-2">€{tx.euro_amount}</td>
                <td className="px-4 py-2">{tx.gold_grams}g</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 rounded ${
                    tx.status === 'completed' ? 'bg-green-100 text-green-800' : 
                    tx.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800'
                  }`}>
                    {tx.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
