import React, { useState } from 'react';
import {
  Flex,
  Button,
  Input,
  useToast,
  Box,
  Text
} from '@chakra-ui/react';
import CacheToggle from './CacheToggle';
import LedPopup from './LedPopup';
import { FiUploadCloud } from 'react-icons/fi';

export const ControlsPane = ({ ws, mode, setMode, setHexCode, setStrip, setSyncDelay, syncDelay}) => {
  const [file, setFile] = useState(null);
  const toast = useToast();

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

    const handleDrop = (e) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        setFile(droppedFile);
      }
    };
  
    const handleDragOver = (e) => {
      e.preventDefault();
    };
  
    const handleFirmwareUpload = () => {
      if (!file) {
        toast({
          title: 'No file selected',
          status: 'warning',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      // Implement actual firmware upload logic here
      toast({
        title: `Firmware file "${file.name}" ready to be uploaded`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    };

  return (
    <Flex direction='column' gap={4} ml={2}>
              <CacheToggle ws={ws}></CacheToggle>

              {/* Clear Cache */}
              <Button onClick={() => {
                if (ws) {
                  ws.send("loadTest") 
                }
                }}>Clear Cache</Button>

              {/* Led Popup */}
              <LedPopup></LedPopup>

              {/* Load Test */}
              <Button onClick={() => {
                if (ws) {
                  ws.send("loadTest") 
                }
                }}>Load Test</Button>

              {/* Display Off */}
                <Button onClick={() => {
                if (ws) {
                  ws.send("allOff") 
                  ws.send("getClientState")
                }
                }}>Display Off</Button>

                {/* Set Color */}
                <Flex direction={"row"} gap={2}>
                  <Button onClick={() => {
                    if (mode !== "color") {
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

                {/* DELETE & RESET */}
                <Flex direction={"row"} gap={2}>

                <Button onClick={() => {
                  if (mode !== "delete") {
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

                {/* Reset */}
                <Button onClick={() => {
                  if (mode !== "reset") {
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
                
               {/*  MODES SELECT */}
              <Flex direction={"row"} gap={2}>

                <Button onClick={() => {
                    if (mode !== "all") {
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
                  if (mode !== "syncOn") {
                    if (mode === "all") {
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
                  if (mode !== "syncOff") {
                    if (mode === "all") {
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

                {/* SYNC TIME DELAY */}
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
                    if (mode !== "singlesync") {
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

                {/* UPDATE FIRMWARE */}
                <Flex direction="row" gap={2} align="center">
                <Button
                  w="50%"
                  variant={"outline"}
                  boxShadow={"0 0 0 1px rgba(239, 207, 227, 1.0)"}
                  // borderRadius="lg"
                  // borderWidth={"1px"}
                  // borderStyle="solid"
                  // borderColor="blue.300"
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  flexDirection="column"
                  cursor="pointer"
                  bg="gray.1"
                  _hover={{ borderColor: "pink.400", bg: "rgba(239, 207, 227, .2)" }}
                >
                  <FiUploadCloud size={18} color="gray" />
                  <Text fontSize="sm" mt={.5}>
                    {file ? file.name : "Drag & Drop"}
                  </Text>
                </Button>
                
                <Button
                  colorScheme="pink"
                  onClick={handleFirmwareUpload}
                  w="50%"
                >
                  Add Firmware
                </Button>
              </Flex>

                {/* VIEW INFO */}
                <Flex direction={"row"} gap={2}>

                {/* Reset */}
                <Button onClick={() => {
                  if (mode !== "info") {
                    setMode("info") 
                  } else {
                    setMode("") 
                  }
                }}
                variant={mode === "info" ? "solid" : "outline"}
                colorScheme="purple"
                boxShadow={mode === "info" ? "0 0 0 3px rgba(120, 0, 180, 0.6)" : "none"}
                w={"50%"}
                >
                View Info
                </Button>
                </Flex>


            </Flex>
  );
};
