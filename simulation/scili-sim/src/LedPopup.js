import React from 'react';
import LedBuilding from './LedBuilding';
import ReactDOM from 'react-dom/client'; // Import ReactDOM
import { Button } from '@chakra-ui/react';

const LedPopup = () => {
  const openPopup = () => {
    // Open a new browser window with the LedBuilding component
    const popupWindow = window.open("https://kazar4.com/SciliTetris/simulationHTML/index.html", '_blank', 'width=150,height=400')
    //window.open('', '_blank', 'width=200,height=400');
    

    
    const popupContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>LED Building Sim</title>
        <style>
          html, body {
            margin: 0;
            padding: 0;
            background-color: #4A5568; /* Set background color */
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          #led-popup-container {
            width: 80%;
            height: 80%;
          }
        </style>
      </head>
      <body>
        <div id="led-popup-container"></div>
      </body>
      </html>
    `;

    // // Write the content to the new window
    // popupWindow.document.write(popupContent);

    // // Render the LedBuilding component in the container
    // const ledPopupContainer = popupWindow.document.getElementById('led-popup-container');
    // ledPopupContainer && ReactDOM.createRoot(ledPopupContainer).render(<LedBuilding />);
    //ledPopupContainer && ReactDOM.render(<LedBuilding />, ledPopupContainer);
  };

  return (
    <div>
      <Button onClick={openPopup}>Open LED Building</Button>
    </div>
  );
};

export default LedPopup;