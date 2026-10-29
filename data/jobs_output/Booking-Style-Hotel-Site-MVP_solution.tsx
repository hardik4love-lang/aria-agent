// Hotel Booking Search & Availability Filter
'use client';
import React, { useState } from 'react';

export default function HotelSearchComponent() {
  const [destination, setDestination] = useState('');
  const [guests, setGuests] = useState(2);

  const sampleHotels = [
    { id: 1, name: "Grand Vista Palace", rating: 4.8, pricePerNight: 120, location: "Downtown" },
    { id: 2, name: "Azure Beach Resort", rating: 4.9, pricePerNight: 185, location: "Seaside" }
  ];

  return (
    <div className="p-6 bg-slate-50 rounded-xl max-w-3xl mx-auto border border-slate-200">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <input
          type="text"
          placeholder="Where are you going?"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <select value={guests} onChange={(e) => setGuests(Number(e.target.value))} className="p-3 border rounded-lg">
          <option value={1}>1 Guest</option>
          <option value={2}>2 Guests</option>
          <option value={4}>4 Guests</option>
        </select>
        <button className="bg-blue-600 text-white font-bold p-3 rounded-lg hover:bg-blue-700 transition-all">Search Deals</button>
      </div>
      <div className="space-y-4">
        {sampleHotels.map(h => (
          <div key={h.id} className="p-4 bg-white rounded-lg shadow-sm flex justify-between items-center border">
            <div>
              <h3 className="font-bold text-lg text-slate-800">{h.name}</h3>
              <p className="text-sm text-slate-500">{h.location} • {h.rating} ★</p>
            </div>
            <div className="text-right">
              <span className="text-xl font-bold text-blue-600">${h.pricePerNight}</span>
              <span className="text-xs text-slate-400 block">/ night</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
