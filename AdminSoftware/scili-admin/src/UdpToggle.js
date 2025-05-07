import { useEffect, useState } from 'react';
import { Button, Box, Flex, Text, Switch } from '@chakra-ui/react';

const UdpToggle = ({ws, udpState, setUdpState}) => {


 

  const handleChange = () => {
    setUdpState(!udpState);

    if (ws) {
      ws.send("udpToggle")
    }
  };

  // useEffect(() => { 

  //   console.log(udpState)
  //   console.log(isUdpOn)

  // if (udpState === isUdpOn) {
  //   setUdpString((udpState ? "UDP On" : "UDP Off") + "  ✅")
  // }

  // }, [udpState])

  return (

    <Flex dir='row' gap={3}>
      {/* <Switch
            colorScheme="green"
            isChecked={isUdpOn}
            onChange={handleChange}
            size="lg"
          /> */}

        <Button fontSize="14px" textAlign={"center"} onClick={handleChange}>
          {(udpState ? "UDP On" : "UDP Off")}
        </Button>
    </Flex>
   
  );
};

export default UdpToggle;