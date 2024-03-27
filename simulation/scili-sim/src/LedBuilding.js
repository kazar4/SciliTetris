import React from 'react';
import LedBlock from './LedBlock';

const LedBuilding = () => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 20px)', gridTemplateRows: 'repeat(14, 20px)' }}>
      {Array.from({ length: 5 }, (_, row) =>
        Array.from({ length: 14 }, (_, column) => (
          <LedBlock key={`${row}-${column}`} row={row} column={column} />
        // <div>hi</div>
        ))
      )}
    </div>
  );
};

export default LedBuilding;