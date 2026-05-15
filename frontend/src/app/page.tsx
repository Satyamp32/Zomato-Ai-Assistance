"use client";

import { useState } from 'react';

type Recommendation = {
  restaurant_name: string;
  explanation: string;
};

type APIResponse = {
  status: string;
  message: string;
  candidates_analyzed: number;
  recommendations: Recommendation[];
};

const BANGALORE_LOCATIONS = [
  "Indiranagar", "Koramangala", "Bellandur", "Whitefield", "Jayanagar", 
  "HSR Layout", "JP Nagar", "Marathahalli", "Malleshwaram", "Banashankari", 
  "Electronic City", "BTM Layout", "Richmond Road", "Sarjapur Road"
];

const POPULAR_CUISINES = [
  "Any", "North Indian", "South Indian", "Chinese", "Italian", "Continental", 
  "Desserts", "Beverages", "Cafe", "Fast Food", "Street Food", "Asian", "Mediterranean"
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<APIResponse | null>(null);

  const [location, setLocation] = useState('Bellandur');
  const [budget, setBudget] = useState('high');
  const [cuisine, setCuisine] = useState('Any');
  const [minRating, setMinRating] = useState('4.0');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    const payload = {
      location,
      budget,
      cuisines: cuisine !== 'Any' ? [cuisine] : [],
      min_rating: parseFloat(minRating) || 0,
      additional_text: ""
    };

    try {
      let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/recommendations';
      
      // Fix: If the user provided the URL without http/https, prepend https://
      if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
        apiUrl = 'https://' + apiUrl;
      }

      // Fix: If the user provided the base URL without the endpoint path, append it automatically
      if (!apiUrl.endsWith('/api/v1/recommendations')) {
        apiUrl = apiUrl.replace(/\/$/, '') + '/api/v1/recommendations';
      }

      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`API returned ${res.status}. Please check if the Railway backend is awake.`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to the backend API.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <header>
        <h1>Zomato AI Assistant</h1>
        <p>Discover your next favorite restaurant with personalized AI recommendations.</p>
      </header>

      <div className="container">
        {/* Form Section */}
        <section className="glass-panel">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Location (Bangalore)</label>
              <select value={location} onChange={(e) => setLocation(e.target.value)} required>
                {BANGALORE_LOCATIONS.sort().map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Budget</label>
              <select value={budget} onChange={(e) => setBudget(e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="form-group">
              <label>Cuisine</label>
              <select value={cuisine} onChange={(e) => setCuisine(e.target.value)}>
                {POPULAR_CUISINES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Minimum Rating (0-5)</label>
              <input 
                type="number" 
                step="0.1" 
                min="0" 
                max="5"
                value={minRating} 
                onChange={(e) => setMinRating(e.target.value)} 
              />
            </div>

            <button type="submit" disabled={loading}>
              {loading ? 'Analyzing Options...' : 'Get Recommendations'}
            </button>
          </form>
        </section>

        {/* Results Section */}
        <section>
          {loading && (
            <div className="empty-state">
              <div className="loader"></div>
              <p style={{ marginTop: '2rem' }}>Our AI is curating the best options for you...</p>
            </div>
          )}

          {error && (
            <div className="status-box">
              <h3>Error</h3>
              <p>{error}</p>
            </div>
          )}

          {result && result.status === 'no_candidates' && (
            <div className="status-box">
              <h3>No Matches Found</h3>
              <p>{result.message}</p>
            </div>
          )}

          {result && result.status === 'success' && (
            <div>
              <h2 className="results-header">Top Recommendations</h2>
              <div className="recommendations">
                {result.recommendations.map((rec, idx) => (
                  <div key={idx} className="card">
                    <h3>{rec.restaurant_name}</h3>
                    <p>{rec.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && !error && !result && (
            <div className="empty-state">
              <p>Fill out the form on the left to get AI-powered recommendations.</p>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
