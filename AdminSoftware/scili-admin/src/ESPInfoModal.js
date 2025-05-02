import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  Badge,
  Text,
  Stack,
  Center,
  Icon,
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';

const EspInfoModal = ({ isOpen, onClose, modalInfo }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} motionPreset="slideInBottom" size="md">
      <ModalOverlay />
      <ModalContent borderRadius="2xl" p={4}>
      <ModalHeader>
  <Center flexDirection="column">
  <Icon as={InfoIcon} boxSize={8} color="blue.500" mb={2} />
    <Text fontSize="2xl" fontWeight="bold">ESP Device Info</Text>
  </Center>
</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Stack spacing={4}>

            <Text>
              <strong>ESP ID:</strong> 
              <Badge colorScheme="green" fontSize="1em" ml={2}>
                {modalInfo?.esp || 'Unknown'}
              </Badge>
            </Text>

            <Text>
              <strong>Firmware:</strong> 
              <Badge colorScheme="purple" fontSize="1em" ml={2} textTransform="none">
                {modalInfo?.firmware || 'Unknown'}
              </Badge>
            </Text>

          
            {modalInfo?.ping && (
            <Text>
              <strong>Ping:</strong> 
              <Badge colorScheme="red" fontSize="1em" ml={2} textTransform="none">
                {modalInfo?.ping}ms
              </Badge>
            </Text>
            )}

          </Stack>
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default EspInfoModal;
