import React from 'react';
import LedBlock from './LedBlock';
import {
  ChakraProvider,
  Box,
  Text,
  Link,
  VStack,
  Code,
  Grid,
  theme,
  Flex
} from '@chakra-ui/react';

const LedBuilding = () => {
  return (
    
    <Box
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        width: '100%',  // Full width
        height: '100%', // Full height
      }}
    >
    <Box style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 20px)', gridTemplateRows: 'repeat(14, 20px)' }}>
      {Array.from({ length: 5 }, (_, row) =>
        Array.from({ length: 11 }, (_, column) => (
          <LedBlock key={`${row}-${column}`} row={row} column={column} />
        // <div>hi</div>
        ))
      )}
    </Box>
    </Box>
  );
};

export default LedBuilding;