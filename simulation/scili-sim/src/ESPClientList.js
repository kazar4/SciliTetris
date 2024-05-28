import React, { useState, useEffect } from 'react';
import { List, ListItem, ListIcon, Button, Text, Box, Flex, Icon } from '@chakra-ui/react';
import { CheckCircleIcon, SunIcon } from '@chakra-ui/icons';
import { DndProvider, useDrag } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import * as ReactIcons from 'react-icons/io';

const EspClientList = ({ ws, wsRes, xDimension, yDimension }) => {
  const [espClients, setEspClients] = useState([]); // List of ESP clients
  const [selectedClient, setSelectedClient] = useState(null); // Selected ESP client


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

//   useEffect(() => {

//     if (ws) {
//         ws.onmessage = (event) => {
//             const message = JSON.parse(event.data);
//             if (message.type === 'getClientState') {
//               // Update the LED list based on the received JSON data
//               console.log("got client state")
//               updateEspClients(message.data);
//             }
//           };
//     }

//     return () => {
//     };
//   }, [ws]);

  const updateEspClients = (clientData) => {
    // Process the JSON data received from the server and update the LED list
    let updatedClients = clientData.map(client => ({
      key: client.clientName,
      id: client.clientName,
      x: client.x1,
      y: client.y1,
      color: client.color
    }));

    updatedClients = updatedClients.filter(client => {
        //console.log(client.y)
        return (client.x === null && client.y === null) || client.x >= xDimension * 2 || client.y >= yDimension
    })

    // [(), (), (), (), ()]
    for (let val in updatedClients) {
      console.log(val)
      if (clientData[val].color !== "F000000") {
        console.log(`(${val["x1"]} ${val["y1"]}), (${val["x2"]}, ${val["y2"]})`)
      }
    }

    setEspClients(updatedClients);
  };

  const handleRefresh = () => {
    // Send "getClientState" message again to refresh the data
    if (ws) {
      console.log('Refreshing data...');
      ws.send("getClientState");
    }
  };
  
  const handleCheck = () => {
    // Send "getClientState" message again to refresh the data
    if (ws) {
      console.log('Checking data...');
      ws.send("checkClientConnections");
    }
  };
  const handleSetColor = (clientId) => {
    // Send "setColor" command for the selected client ID
    if (ws) {
      console.log(`Setting color for client ${clientId}`);
      ws.send(`setColor ${clientId} #FF00FF`);
    }
  };

  return (
    <Box>
        <Box>
                <Text mb={2}>ESP Clients</Text>
                <Button onClick={handleRefresh} mt={3}>Refresh</Button>
                <Button onClick={handleCheck} mt={3}>Check Connections</Button>
            </Box>
    <Flex flexWrap={"wrap"} maxHeight="calc(75vh - 20px)" overflowY="auto">
      {/* Clients Grid */}

          {espClients.map((client, index) => (
            <Box width="33.33%">
                <DraggableClient 
                    key={index} 
                    i={index} 
                    client={client}
                    handleSetColor={handleSetColor} 
                    ws={ws}
                    xDimension={xDimension}
                    yDimension={yDimension}
                    />
            </Box>
          ))}

    </Flex>
    </Box>

  );
};

const DraggableClient = ({ i, client, handleSetColor, ws, xDimension, yDimension }) => {
    const [{ isDragging }, drag] = useDrag({
        type: 'ledDisplay', // Define the type property here
        collect: (monitor) => ({
          isDragging: !!monitor.isDragging(),
        }),
        item: () => {
            console.log('Dragging started ' + client.id); // Log when dragging starts

            ws.send(`setColor ${client.id} #FF0000`)

            return { espID: client.id }; // Assuming you need to pass client id as the item
          },
        end: (item, monitor) => {

        // console.log("Is this always running")
        ws.send(`setColor ${client.id} #000000`)

        if (monitor.didDrop()) {
            console.log("Is it repeating this")

            ws.send(`setColor ${client.id} #00FF00`)
            // Run your function here when dragging ends and an item is dropped
            console.log('Dragging ended');
            ws.send("getClientState");
        }
        }
      });

      function getRandomIcon(index) {
        // Get all icons from the ReactIcons object
        const icons = Object.values(ReactIcons);

        //console.log(icons)

        let randomIcon = null;

        if (icons.length - 1 < index) {
            randomIcon = icons[Math.floor(Math.random() * icons.length)];
        } else {
            randomIcon = icons[index];
        }
      
        return randomIcon;
      }

      //console.log(getRandomIcon())

      let borderColor = client.x >= xDimension * 2 || client.y >= yDimension ? "red" : "white"

  return (
    <Box ref={drag} cursor="pointer" border={`1px solid ${borderColor}`} borderRadius={"10px 10px 10px 10px"} margin={1}>
      {/* <ListIcon as={CheckCircleIcon} /> */}
      <Icon as={getRandomIcon(i)}/> { }
      {client.id}
      {/* <Box onClick={() => handleSetColor(client.id)} ml={2} cursor="pointer">
        <SunIcon />
      </Box> */}
    </Box>
  );
};

export default EspClientList;
