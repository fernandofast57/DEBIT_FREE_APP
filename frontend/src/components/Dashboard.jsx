
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [transformations, setTransformations] = useState([]);
  const [balance, setBalance] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [transformRes, balanceRes] = await Promise.all([
          axios.get('/api/v1/transformations'),
          axios.get('/api/v1/gold/balance')
        ]);
        setTransformations(transformRes.data);
        setBalance(balanceRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gold Investment Dashboard</h1>
      <TransformationForm />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl mb-2">Current Balance</h2>
          <p className="text-3xl font-bold">{balance?.balance || 0} g</p>
        </div>
        <NotificationList />
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-xl mb-4">Recent Transformations</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th>Date</th>
              <th>Amount (EUR)</th>
              <th>Gold (g)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {transformations.map(t => (
              <tr key={t.id}>
                <td>{new Date(t.created_at).toLocaleDateString()}</td>
                <td>{t.euro_amount}</td>
                <td>{t.gold_grams}</td>
                <td>{t.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
