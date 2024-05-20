import React, { useState, useEffect, createRef } from 'react';
import {
  ChakraProvider,
  Box,
  Text,
  Link,
  VStack,
  Code,
  Grid,
  theme,
  Flex,
  Textarea,
  Button,
  Input
} from '@chakra-ui/react';
import { ColorModeSwitcher } from './ColorModeSwitcher';
import { Logo } from './archive/Logo';
import LedBuilding from './LedBuilding';
import LedPopup from './LedPopup';
import LedDisplay from './LedDisplay';
import EspClientList from './ESPClientList';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { DndProvider } from 'react-dnd';
import CacheToggle from './CacheToggle';

function App() {

  const [ws, setWs] = useState(null); // WebSocket connection
  const [wsRes, setWsRes] = useState(null);

  const [mode, setMode] = useState("");
  const [hexCode, setHexCode] = useState('');
  const [strip, setStrip] = useState('3');
  const [syncDelay, setSyncDelay] = useState("");

  const [xDimension, setXDimension] = useState(5); // Initial x dimension
  const [yDimension, setYDimension] = useState(11); // Initial y dimension

  const textBoxRef = React.createRef();

   // Function to handle changes in the input value
   const handleInputChange = (event) => {
    // Update the hexCode state with the new value entered by the user
    setHexCode(event.target.value);
  };

  const handleStripChange = (event) => {
    // Update the hexCode state with the new value entered by the user
    setStrip(event.target.value);
  };

  const handleSyncChange = (event) => {
    // Update the hexCode state with the new value entered by the user
    setSyncDelay(event.target.value);
  };



  useEffect(() => {
     const websocket = new WebSocket('ws://brown.proteinarium.edu:4567');
    //const websocket = new WebSocket('ws://localhost:9001')

    websocket.onopen = () => {
      console.log('WebSocket connection established.');
      setWs(websocket); // Store WebSocket connection in state
      websocket.send("admin")
      websocket.send("getClientState")
    };
    websocket.onclose = () => {
      console.log('WebSocket connection closed.');
    };
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log(message)
      setWsRes(message);
    };
    return () => {
      // Close WebSocket connection when component unmounts
      if (ws) {
        console.log("websocket is closing, i'm not sure why")
        ws.close();
      }
    };
  }, []); // Empty dependency array ensures this effect runs only once on component mount


  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">

      {/* <Flex alignContent={"center"} justifyContent={"center"} mt={"10%"}> */}
        {/* <LedBuilding></LedBuilding> */}

        {/* <DndProvider backend={HTML5Backend}>

          <LedDisplay ws={ws} wsRes={wsRes}></LedDisplay>

          <LedPopup></LedPopup>

          <EspClientList ws={ws} wsRes={wsRes}></EspClientList>

        </DndProvider> */}
      {/* </Flex> */}

      <ColorModeSwitcher justifySelf="flex-end" />
      <DndProvider backend={HTML5Backend}>
        <Flex direction="column" height="100vh">
        {/* Top section */}
        <Flex justify="space-between" align="center" height="10%">
        <ColorModeSwitcher justifySelf="flex-end" />
          <Box flex="0 0 20%"></Box>
          <Box flex="0 0 60%" textAlign="center">Scili Admin Controls</Box>
          <Box flex="0 0 20%" textAlign="right"></Box>
        </Flex>
        
        {/* Middle section */}
        <Flex height="60%">
          <Box flex="0 0 30%">
            
            <Text mb={6}>Controls</Text>

            <Flex direction='column' gap={4} ml={2}>
              <CacheToggle ws={ws}></CacheToggle>

              <Button onClick={() => {
                if (ws) {
                  ws.send("loadTest") 
                }
                }}>Clear Cache</Button>

              <LedPopup></LedPopup>
              <Button onClick={() => {
                if (ws) {
                  ws.send("loadTest") 
                }
                }}>Load Test</Button>

                <Button onClick={() => {
                if (ws) {
                  ws.send("allOff") 
                  ws.send("getClientState")
                }
                }}>Display Off</Button>

                <Flex direction={"row"} gap={2}>
                  <Button onClick={() => {
                    if (mode != "color") {
                      setMode("color") 
                    } else {
                      setMode("") 
                    }
                }}
                  variant={mode === "color" ? "solid" : "outline"}
                  colorScheme="blue"
                  boxShadow={mode === "color" ? "outline" : "none"}
                  >Color</Button>
                  <Input placeholder="Hex Code #FFFFFF" fontSize={13} onChange={handleInputChange}></Input>
                  <Input placeholder="S" w={"30%"} onChange={handleStripChange}></Input>
                </Flex>


                <Flex direction={"row"} gap={2}>

                <Button onClick={() => {
                  if (mode != "delete") {
                    setMode("delete") 
                  } else {
                    setMode("") 
                  }
                }}
                variant={mode === "delete" ? "solid" : "outline"}
                colorScheme="blue"
                boxShadow={mode === "delete" ? "outline" : "none"}
                w={"50%"}
                >
                Delete
                </Button>

                <Button onClick={() => {
                  if (mode != "reset") {
                    setMode("reset") 
                  } else {
                    setMode("") 
                  }
                }}
                variant={mode === "reset" ? "solid" : "outline"}
                colorScheme="orange"
                boxShadow={mode === "reset" ? "0 0 0 3px rgba(246, 173, 85, 0.6)" : "none"}
                w={"50%"}
                >
                Reset
                </Button>

                </Flex>
                
                
              <Flex direction={"row"} gap={2}>

                <Button onClick={() => {
                    if (mode != "all") {
                      setMode("all") 
                    } else {
                      setMode("") 
                    }
                  }}
                  variant={mode === "all" ? "solid" : "outline"}
                  colorScheme="blue"
                  boxShadow={mode === "all" ? "outline" : "none"}
                  w={"50%"}
                  >
                  All
                  </Button>

                <Button onClick={() => {
                  if (mode != "syncOn") {
                    if (mode == "all") {
                      ws.send("syncOn all")
                      setMode("") 
                    } else {
                      setMode("syncOn") 
                    }
                  } else {
                    setMode("") 
                  }
                }}
                variant={mode === "syncOn" ? "solid" : "outline"}
                colorScheme="green"
                boxShadow={mode === "syncOn" ? "outline" : "none"}
                w={"50%"}
                >
                syncOn
                </Button>

                <Button onClick={() => {
                  if (mode != "syncOff") {
                    if (mode == "all") {
                      ws.send("syncOff all")
                      setMode("") 
                    } else {
                      setMode("syncOff") 
                    }
                  } else {
                    setMode("") 
                  }
                }}
                variant={mode === "syncOff" ? "solid" : "outline"}
                colorScheme="red"
                boxShadow={mode === "syncOff" ? "0 0 0 3px rgba(246, 173, 85, 0.6)" : "none"}
                w={"50%"}
                >
                syncOff
                </Button>

                </Flex>


                <Flex direction={"row"} gap={2}>

                <Input placeholder="Sync Time Delay (ms)" fontSize={11} onChange={handleSyncChange}></Input>


                <Button onClick={() => {
                  if (syncDelay !== "") {
                    ws.send(`sync all ${syncDelay}`)
                  }
                }}
                variant={mode === "syncall" ? "solid" : "outline"}
                colorScheme="blue"
                boxShadow={mode === "syncall" ? "outline" : "none"}
                w={"50%"}
                >
                Send All
                </Button>

                <Button onClick={() => {
                    if (mode != "singlesync") {
                      setMode("singlesync") 
                    } else {
                      setMode("") 
                    }
                }}
                variant={mode === "singlesync" ? "solid" : "outline"}
                colorScheme="blue"
                boxShadow={mode === "singlesync" ? "outline" : "none"}
                w={"50%"}
                >
                Set Single
                </Button>

                </Flex>


            </Flex>
          </Box>
          <Box flex="0 0 40%" textAlign="center">
            <LedDisplay 
              ws={ws} 
              wsRes={wsRes}
              mode={mode} 
              hexCode={hexCode}
              strip={strip}
              syncDelay={syncDelay}
              xDimension={xDimension}
              setXDimension={setXDimension}
              yDimension={yDimension}
              setYDimension={setYDimension}
              >
              </LedDisplay></Box>
          <Box flex="0 0 30%" textAlign="center" justifyContent={"center"}>
            <EspClientList ws={ws} wsRes={wsRes} xDimension={xDimension} yDimension={yDimension}></EspClientList>
            </Box>
        </Flex>
        


      </Flex>
        {/* Bottom section */}
        <Flex height="20%" align="center" pt={5}>
          <Textarea width="100%" placeholder="Enter text here" ref={textBoxRef}
          onKeyDown={(e) => {

            let key = e.key;

            // If the user has pressed enter
            if (key === 'Enter') {
              if (ws) {
                ws.send(textBoxRef.current.value) 
                ws.send("getClientState")
              }
            }
            else {
                return true;
            }
            }}
          />
        </Flex>
    </DndProvider>

        {/* <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Logo h="40vmin" pointerEvents="none" />
            <Text>
              Edit <Code fontSize="xl">src/App.js</Code> and save to reload.
            </Text>
            <Link
              color="teal.500"
              href="https://chakra-ui.com"
              fontSize="2xl"
              target="_blank"
              rel="noopener noreferrer"
            >
              Learn Chakra
            </Link>
          </VStack>
        </Grid> */}
      </Box>
    </ChakraProvider>
  );
}

export default App;
