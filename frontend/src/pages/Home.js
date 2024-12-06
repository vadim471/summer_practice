import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Home() {
  const [apartments, setApartments] = useState([]);

  useEffect(() => {
    axios.get('/api/apartments')
      .then(response => {
        setApartments(response.data);
      })
      .catch(error => {
        console.error("There was an error fetching the apartments!", error);
      });
  }, []);

  return (
    <div>
      <h1>Available Apartments</h1>
      <ul>
        {apartments.map(apartment => (
          <li key={apartment.id}>
            {apartment.street} {apartment.house}, {apartment.rooms_count} rooms, {apartment.floor} floor, {apartment.square} m²
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Home;