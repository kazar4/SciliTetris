import React, { useState, useEffect } from 'react';
import { Box, Grid, Input, Flex, Text } from '@chakra-ui/react';
import { DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { 
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  Button, Stack, Badge, Icon, Center, useDisclosure
} from '@chakra-ui/react';
import EspInfoModal from './ESPInfoModal';


const LedDisplay = ({ws, wsRes, mode, hexCode, strip, syncDelay, xDimension, yDimension, setXDimension, setYDimension, setLedPerESP, ledPerESP, setBatchDelay, setUdpState}) => {
    
  const [espClients, setEspClients] = useState({}); // List of ESP clients from x,y
  //const [espDict, setEspDict] = useState(());

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [modalInfo, setModalInfo] = useState({});

  const [colorToggle, setColorToggle] = useState(false)
  const [pingToggle, setPingToggle] = useState(true)

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

            setLedPerESP(wsRes["LEDPerEsp"])
            setBatchDelay(wsRes["batchDelay"])
            updateEspClients(wsRes.data);
          }

          if (wsRes.type === 'update') {
            // Update the LED list based on the received JSON data
            console.log("got update request")
            ws.send("getClientState")
          }

          if (wsRes.type === 'udp') {
            //TODO update UDP toggle
            setUdpState(Boolean(wsRes["value"]))
          }

          if (wsRes.type === 'info') {

            let matchingESP = {}
            for (let coord in espClients) {
              if (espClients[coord].id === wsRes.esp){
                matchingESP = espClients[coord]
              }
            }

            // alert(`
            //   EPS INFO:

            //   ESP: ${wsRes.esp}
            //   firmware: ${wsRes.firmware}
            //   ping: ${matchingESP.ping}
              
            //   `)
            setModalInfo({
              esp: wsRes.esp,
              firmware: wsRes.firmware,
              ping: matchingESP.ping,
              udpPing: matchingESP.udpPing
            });
            onOpen();
          }
    
    }
    
    return () => {
    
    };
  }, [wsRes]);


  const updateEspClients = (clientData) => {
    // Normalize clients with their list of coords
    let espStorage = {}
  
    clientData.forEach(client => {
      const clientId = client.clientName;
      const ping = client.ping;
      const udpPing = client.udpPing;

      console.log(client)
  
      // Each client has a variable list of coords, each with x, y, color
      // TODO: this entire for loop part is redudant, I can just pass coords and color

      let x = client.coords[0][0]
      let y = client.coords[0][1]
  
      if (Array.isArray(client.coords) && x !== null && y !== null) {
        espStorage[`${x},${y}`] = {
          id: clientId,
          coords: client.coords,
          colors: client.colors,
          ping,
          udpPing
        };
      }
    });
  
    console.log("espStorage")
    console.log(espStorage);
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

        <Flex flexDir={'row'} gap={3}>
        <Grid templateRows={`repeat(${yDimension}, 45px)`} gap={1} mt={5} mb={4} height={yDimension * 50}>
          {Array.from({ length: yDimension }, (_, index) => (
            <p>{yDimension - index + 2}</p>
          ))}
        </Grid>
        <Grid templateColumns={`repeat(${xDimension}, 45px)`} templateRows={`repeat(${yDimension}, 45px)`} gap={1} mt={5} mb={4} height={yDimension * 45}>
          {Array.from({ length: yDimension * xDimension }, (_, index) => (
            <DroppableBox 
                key={index} 
                index={index} 
                xDimension={xDimension} 
                yDimension={yDimension} 
                ws={ws} 
                wsRes={wsRes}
                espClients={espClients}
                mode={mode} 
                hexCode={hexCode}
                strip={strip}
                syncDelay={syncDelay}
                ledPerESP={ledPerESP}
                colorToggle={colorToggle}
                pingToggle={pingToggle}
                />
          ))}
        </Grid>
        </Flex>

        <Button onClick={() => {
          console.log("Toggling Color to: " + !colorToggle)
          setColorToggle(!colorToggle)
          }}>Toggle Colors</Button>

        <Button mt="10px" onClick={() => {
          console.log("Toggling Ping to: " + !pingToggle)
          setPingToggle(!pingToggle)
          }}>Toggle Ping</Button>

        {/* ESP INFORMATION MODAL */}
        <EspInfoModal
          isOpen={isOpen}
          onClose={onClose}
          modalInfo={modalInfo}
        />
          
      </Flex>
  );
};

const DroppableBox = ({ index, xDimension, yDimension, ws, wsRes, espClients, mode, hexCode, strip, syncDelay, ledPerESP, colorToggle, pingToggle}) => {

    const [assignedESP, setAssignedESP] = useState([]); // List of ESP clients
    const [textDiv, setTextDiv] = useState("");
    const [colorDefault, setColorDefault] = useState("transparant");
    const [boxBG, setBoxBG] = useState("transparant");
    const [subText, setSubText] = useState("");

    const handleDrop = (index) => {
        return (item, monitor) => {
          // Handle drop event here

          let x = index % xDimension
          let y = Math.floor((index) / xDimension)

          // So ledPerESP is important here now
          // Before this was 2

          console.log(`setCoords ${item.espID} ${x * ledPerESP} ${y}`)
          console.log(`Dropped item ${item.type} onto LED box ${index} with id ${item.espID}`);


          ws.send(`setCoords ${item.espID} ${x * ledPerESP} ${y}`)
          ws.send('getClientState')
          // Optionally, you can return a drop result here if needed
        };
      };

      function blendColors(colorA, colorB, amount) {
        console.log("got here")
        console.log(colorA)
        console.log(colorB)
        console.log(colorA.match(/\w\w/g).map((c) => parseInt(c, 16)))
        let [rA1, gA1, bA1] = colorA.match(/\w\w/g).map((c) => parseInt(c, 16));

        if (colorA === "#000000") {
          return colorB;
        }
    
        if (colorB === "#000000") {
          return colorA;
        }
    
        const [rA, gA, bA] = colorA.match(/\w\w/g).map((c) => parseInt(c, 16));
        const [rB, gB, bB] = colorB.match(/\w\w/g).map((c) => parseInt(c, 16));
        const r = Math.round(rA + (rB - rA) * amount).toString(16).padStart(2, '0');
        const g = Math.round(gA + (gB - gA) * amount).toString(16).padStart(2, '0');
        const b = Math.round(bA + (bB - bA) * amount).toString(16).padStart(2, '0');
        return '#' + r + g + b;
      }
      
      // So we have a grid of 5 x 11
      // we expanded it to 10 x 11
      // so we are receiving pixels in the 10 x 11 space
      // but in terms of finding a match
      // (0,0) and (1,0) should map to (0,0) and so on
      // (2,0) and (3,0) to (1,0)
      // But I coded it so only (0,0) -> (0,0) and (2,0)  are actually being saved on our end
      // then (4,0) then (6,0)

      function toggleColors(colors, colorSetter) {

        if (colorToggle) {
          // Build gradient from numOfLeds entries only
          const step = 100 / ledPerESP;
          const gradientParts = colors.map((color, i) => {
            const start = i * step;
            const end = start + step;
            return `${color} ${start}%, ${color} ${end}%`;
          });

          const gradient = `linear-gradient(90deg, ${gradientParts.join(', ')})`;
          console.log("Setting gradient:", gradient);

          //ledBlock.style.background = gradient;
          //ledBlock.setAttribute("style", `background: ${gradient};`);
          colorSetter(gradient)
        } else {
          colorSetter("transparent")
        }
      }

      useEffect(() => {

        let x = index % xDimension
        let y = Math.floor((index) / xDimension)

        if (`${x*ledPerESP},${y}` in espClients) {
            console.log("found a match")
            let espVal = espClients[`${x*ledPerESP},${y}`]
            console.log(espVal)
            setTextDiv(espVal["id"])
            console.log(espVal)
            console.log(espVal["colors"])
            //setAssignedESP(espVal["id"])
            //let newColor = blendColors(espVal["color1"], espVal["color2"], 0.5)
            //setColorDefault("#FF00FF")

            toggleColors(espVal["colors"], setBoxBG)

            if (espVal["ping"] != null) {
              if (pingToggle) {
                setSubText(espVal["ping"] + "ms")
              } else {
                setSubText(espVal["udpPing"] + "ms")
              }
            }
        } else {
            setTextDiv("")
            setColorDefault("transparant")
            setSubText("")
        }
        
        return () => {
        
        };
      }, [espClients, colorToggle, pingToggle]);
    
      // useEffect(() => {

      //   let x = index % xDimension
      //   let y = Math.floor((index) / xDimension)

      //   if (`${x * ledPerESP},${y}` in espClients) {
      //       console.log("found a match")
      //       let espVal = espClients[`${x * ledPerESP},${y}`]
      //       console.log(espVal)
      //       setTextDiv(espVal["id"])
      //       console.log(espVal["colors"])
      //       //let newColor = blendColors(espVal["color1"], espVal["color2"], 0.5)
      //       //setColorDefault(newColor)
      //   }
        
      //   return () => {
            
      //   };
      // }, []);

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
        let possibleStripVals = Array.from(Array(ledPerESP), (e,i)=>String((i + 1)))
        //  alert(possibleStripVals)
        if (possibleStripVals.includes(strip)) {
          ws.send(`setColor ${x * ledPerESP + (parseInt(strip)) - 1} ${y} ${hexCode}`)
        } else { // actualCoordX = GridX * LedPerESP + Strip - 1           Strip = (ActualCoordX + 1) - (GridX * LEDPerESP)
          // 3 Case
          if (textDiv !== "") {
            ws.send(`setColor ${textDiv} ${hexCode}`)
          } else { 
            console.log("Need to assign esp to color it")
          }
            
          // ws.send(`setColor ${x * 2} ${y} ${hexCode}`)
          // ws.send(`setColor ${x * 2 + (parseInt(strip) - 1)} ${y} ${hexCode}`)
        }
        ws.send("getClientState")
    }

    if (mode === "delete") {
      console.log("trying to delete")
        ws.send(`removeCoord ${textDiv}`)
        ws.send("getClientState")
    }

    if (mode === "reset") {
      ws.send(`removeCoord ${textDiv}`)
      setTimeout(function () {
        ws.send(`reset ${textDiv}`)
        ws.send("getClientState")  
      }, 1000); 

    }

    if (mode === "singlesync") {
      ws.send(`sync ${textDiv} ${syncDelay}`)
    }

    if (mode === "info") {
      ws.send(`info get ${textDiv}`)
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
      // background={boxBG}
      background={isOver ? 'yellow' : boxBG}
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
