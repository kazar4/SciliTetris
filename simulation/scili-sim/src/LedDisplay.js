import React, { useState, useEffect } from 'react';
import { Box, Grid, Input, Flex, Text } from '@chakra-ui/react';
import { DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

const LedDisplay = ({ws, wsRes, mode, hexCode, xDimension, yDimension, setXDimension, setYDimension}) => {
    
  const [espClients, setEspClients] = useState({}); // List of ESP clients

  const handleChangeXDimension = (event) => {
    setXDimension(Number(event.target.value));
  };

  const handleChangeYDimension = (event) => {
    setYDimension(Number(event.target.value));
  };

  useEffect(() => {

    console.log(wsRes)
    if (wsRes) {
        if (wsRes.type === 'getClientState') {
            // Update the LED list based on the received JSON data
            console.log("got client state in LedDisplay")
            updateEspClients(wsRes.data);
          }

          if (wsRes.type === 'update') {
            // Update the LED list based on the received JSON data
            console.log("got update request")
            ws.send("getClientState")
          }

    }
    
    return () => {
    
    };
  }, [wsRes]);


  const updateEspClients = (clientData) => {
    // Process the JSON data received from the server and update the LED list
    let updatedClients = clientData.map(client => ({
      id: client.clientName,
      x: client.x,
      y: client.y,
      color: client.color,
      ping: client.ping
    }));


    const espStorage = {}
    for (let val in clientData) {
        let client = updatedClients[val]
        let id = client.clientName
        let x = client.x
        let y = client.y
        let color = client.olor
        let ping = client.ping

        if (x !== null && y !== null) {
            espStorage[`${x},${y}`] = client
        }
    }

    console.log(espStorage)

    setEspClients(espStorage);
  };

  return (
      <Flex direction="column" alignItems="center" justifyContent={"center"}>
        <Flex justifyContent={"center"}>
          <Box width={"20%"}>
            <Text>X:</Text>
            <label>
              <Input type="number" onChange={handleChangeXDimension}/>
            </label>
          </Box>
          <Box width={"20%"} marginLeft={2}>
            <Text>Y:</Text>
            <label>
              <Input type="number" onChange={handleChangeYDimension}/>
            </label>
          </Box>
        </Flex>
        <Grid templateColumns={`repeat(${xDimension}, 45px)`} templateRows={`repeat(${yDimension}, 45px)`} gap={1} mt={5} mb={4} height={yDimension * 60}>
          {Array.from({ length: yDimension * xDimension }, (_, index) => (
            <DroppableBox 
                key={index} 
                index={index} 
                xDimension={xDimension} 
                yDimension={yDimension} 
                ws={ws} 
                espClients={espClients}
                mode={mode} hexCode={hexCode}
                />
          ))}
        </Grid>
      </Flex>
  );
};

const DroppableBox = ({ index, xDimension, yDimension, ws, espClients, mode, hexCode}) => {

    const [assignedESP, setAssignedESP] = useState([]); // List of ESP clients
    const [textDiv, setTextDiv] = useState("");
    const [colorDefault, setColorDefault] = useState("transparant");
    const [subText, setSubText] = useState("");

    const handleDrop = (index) => {
        return (item, monitor) => {
          // Handle drop event here

          let x = index % xDimension
          let y = Math.floor((index) / xDimension)

          console.log(`setCoords ${item.espID} ${x} ${y}`)
          console.log(`Dropped item ${item.type} onto LED box ${index} with id ${item.espID}`);
          ws.send(`setCoords ${item.espID} ${x} ${y}`)
          ws.send('getClientState')
          // Optionally, you can return a drop result here if needed
        };
      };

      useEffect(() => {

        let x = index % xDimension
        let y = Math.floor((index) / xDimension)

        if (`${x},${y}` in espClients) {
            console.log("found a match")
            let espVal = espClients[`${x},${y}`]
            console.log(espVal)
            setTextDiv(espVal["id"])
            setColorDefault(espVal["color"])
            if (espVal["ping"] != null) {
                setSubText(espVal["ping"] + "ms")
            }
        } else {
            setTextDiv("")
            setColorDefault("transparant")
            setSubText("")
        }
        
        return () => {
        
        };
      }, [espClients]);
    
      useEffect(() => {

        let x = index % xDimension
        let y = Math.floor((index) / xDimension)

        if (`${x},${y}` in espClients) {
            console.log("found a match")
            let espVal = espClients[`${x},${y}`]
            console.log(espVal)
            setTextDiv(espVal["id"])
            setColorDefault(espVal["color"])
        }
        
        return () => {
            
        };
      }, []);

  const [{ isOver }, drop] = useDrop({
    accept: 'ledDisplay',
    drop: handleDrop(index),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  const determineFontSize = (text, size) => {
    // Calculate the ideal font size based on the text length and box dimensions
    const idealFontSize = Math.min(size / text.length, 16); // Adjust the maximum font size as needed
    
    return `${idealFontSize}px`;
  };

  const handleClick = () => {
    let x = index % xDimension
    let y = Math.floor((index) / xDimension)

    console.log(mode === "color" && hexCode.length == 7)

    if (mode === "color" && hexCode.length == 7) {
        ws.send(`setColor ${x} ${y} ${hexCode}`)
        ws.send("getClientState")
    }

    if (mode === "delete") {
        ws.send(`removeCoord ${textDiv}`)
        ws.send("getClientState")
    }

  };

  function getContrastYIQ(hexcolor){
    var r = parseInt(hexcolor.substring(1,3),16);
    var g = parseInt(hexcolor.substring(3,5),16);
    var b = parseInt(hexcolor.substring(5,7),16);
    var yiq = ((r*299)+(g*587)+(b*114))/1000;
    return (yiq >= 128) ? 'black' : 'white';
}

  return (
    <Box
      ref={drop}
      width="45px"
      height="45px"
      border="3px solid white"
      backgroundColor={isOver ? 'yellow' : colorDefault}
      onClick={handleClick}
      cursor={"pointer"}
    >
        <Text fontSize={determineFontSize(textDiv, 45)} color={getContrastYIQ(colorDefault)}>
        {textDiv}
        </Text>

        <Text fontSize={determineFontSize(subText, 45)} color={getContrastYIQ(colorDefault)}>{subText}</Text>

        {/* {index % xDimension}{","}{Math.floor((index) / xDimension)} */}
        </Box>
  );
};

export default LedDisplay;
