import { useState } from 'react';
import { Box, Flex, Text, Switch } from '@chakra-ui/react';

const CacheToggle = ({ws}) => {
  const [isCacheOn, setIsCacheOn] = useState(true);

  const handleChange = () => {
    setIsCacheOn(!isCacheOn);

    if (ws) {
      if (!isCacheOn) {
        ws.send("cacheOn")
      } else{
        ws.send("cacheOff")
      }
    }
  };

  return (

    <Flex dir='row' gap={5}>
      <Text>
        {isCacheOn ? "Cache On" : "Cache Off"}
      </Text>
      <Switch
            colorScheme="teal"
            isChecked={isCacheOn}
            onChange={handleChange}
            size="lg"
          />
    </Flex>
   
  );
};

export default CacheToggle;