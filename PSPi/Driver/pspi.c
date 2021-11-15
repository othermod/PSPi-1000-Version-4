#include "string.h"
#include "pthread.h"
#include "stdio.h"
#include "errno.h"
#include <unistd.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <signal.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <stdbool.h>

#define MCP23017_IODIRA 0x00
#define MCP23017_IPOLA 0x02
#define MCP23017_GPINTENA 0x04
#define MCP23017_DEFVALA 0x06
#define MCP23017_INTCONA 0x08
#define MCP23017_IOCONA 0x0A
#define MCP23017_GPPUA 0x0C
#define MCP23017_INTFA 0x0E
#define MCP23017_INTCAPA 0x10
#define MCP23017_GPIOA 0x12
#define MCP23017_OLATA 0x14

#define MCP23017_IODIRB 0x01
#define MCP23017_IPOLB 0x03
#define MCP23017_GPINTENB 0x05
#define MCP23017_DEFVALB 0x07
#define MCP23017_INTCONB 0x09
#define MCP23017_IOCONB 0x0B
#define MCP23017_GPPUB 0x0D
#define MCP23017_INTFB 0x0F
#define MCP23017_INTCAPB 0x11
#define MCP23017_GPIOB 0x13
#define MCP23017_OLATB 0x15

// pointer register
#define CONV_REG 0
#define CONFIG_REG 1
#define LO_THRESH_REG 2
#define HI_THRESH_REG 3

// bit 15
#define OS_OFF 0
#define OS_ON 0x80

// mono mode
const int analogInput[] = {
  0x40,
  0x50,
  0x60,
  0x70
}; //Analog Selection for 0/1/2/3

// bits 11:9, programmable gains
// gains
#define SIXPT144V 0
#define FOURPT096V 0x2
#define TWOPT048V 0x4
#define ONEPT024V 0x6
#define PT512V 0x8
#define PT256V 0xA

// bit 8, operating mode
// op_mode
#define CONT_MODE 0
#define SNGL_SHOT 1

// bits 7:5, data rate
// dr
#define DR128 0
#define DR250 0x20
#define DR490 0x40
#define DR920 0x60
#define DR1600 0x80
#define DR2400 0xA0
#define DR3300 0xC0

// bit 4, comparator mode
// comp_mode
#define TRAD 0
#define WINDOW 0x10

// bit 3, comp polarity
// comp_pol
#define ACT_LO 0
#define ACT_HI 0x08

// bit 2, comp latching
// comp_latch
#define NON_LATCHING 0
#define LATCHING 0x04

// bits 1-0, comparator queue
// comp_queue
#define ASSERT1 0
#define ASSERT2 0x01
#define ASSERT4 0x02
#define NO_COMP 0x03

int inputSelection;
int inputGain = SIXPT144V;
int operatingMode = SNGL_SHOT;
uint8_t readBuffer[2];
uint8_t writeBuffer[3];
uint8_t mcpReadBuffer[2];
uint16_t previousReadBuffer;
uint16_t ADCstore[4];
int dataRate = DR128;
int comparatorMode = TRAD;
int compPol = ACT_LO;
int compLatch = NON_LATCHING;
int compQueue = NO_COMP;
int verbose = 0;
bool previousState = 1; //if any button was pressed on the last loop, this will be 0
//this was done on every loop, which isnt needed


#define HIGH 1
#define LOW 0
#define INPUT 1
#define OUTPUT 0


bool digitalPinMode(int pin, int dir){
  FILE * fd;
  char fName[128];
  // Exporting the pin to be used
  if(( fd = fopen("/sys/class/gpio/export", "w")) == NULL) {
    printf("Error: unable to export pin\n");
    return false;
  }
  fprintf(fd, "%d\n", pin);
  fclose(fd);
  // Setting direction of the pin
  sprintf(fName, "/sys/class/gpio/gpio%d/direction", pin);
  if((fd = fopen(fName, "w")) == NULL) {
    printf("Error: can't open pin direction\n");
    return false;
  }
  if(dir == OUTPUT) {fprintf(fd, "out\n");} 
	else { fprintf(fd, "in\n");}
  fclose(fd);
  return true;
}

int digitalRead(int pin) {
  FILE * fd;
  char fName[128];
  char val[2];
  // Open pin value file
  sprintf(fName, "/sys/class/gpio/gpio%d/value", pin);
  if((fd = fopen(fName, "r")) == NULL) {
    printf("Error: can't open pin value\n");
    return false;
  }
  fgets(val, 2, fd);
  fclose(fd);
  return atoi(val);
}

int ads1015_open() {
  // open the i2c device
  int file;
  const int ADC_Address = 0x48; //0x48 is the i2c address
  char * filename = "/dev/i2c-0"; //specify which I2C bus to use
  if ((file = open(filename, O_RDWR)) < 0) {
    perror("Failed to open the i2c bus");
    exit(1);
  }

  // initialize the device
  if (ioctl(file, I2C_SLAVE, ADC_Address) < 0) //0x48 is the i2c address
  {
    printf("Failed to acquire bus access and/or talk to slave.\n");
    exit(1);
  }
  return file;
}

int mcp23017_open() {
  // open the i2c device
  int file;
  const int MCP_Address = 0x20; //0x20 is the i2c address
  char * filename = "/dev/i2c-0"; //specify which I2C bus to use
  if ((file = open(filename, O_RDWR)) < 0) {
    perror("Failed to open the i2c bus");
    exit(1);
  }

  // initialize the device
  if (ioctl(file, I2C_SLAVE, MCP_Address) < 0) //0x48 is the i2c address
  {
    printf("Failed to acquire bus access and/or talk to slave.\n");
    exit(1);
  }
  return file;
}

void ads1015SetConfig(int I2C, int input) { //only needs to be done when changing the input
  writeBuffer[1] = OS_ON + analogInput[0] + inputGain + operatingMode;
  if (verbose == 1) printf("writeBuffer[1] : %#x\n", writeBuffer[1]);
  writeBuffer[2] = dataRate + comparatorMode + compPol + compLatch + compQueue;
  if (verbose == 1) printf("Setting Configs. writeBuffer[2] : %#x\n", writeBuffer[2]);

  writeBuffer[0] = CONFIG_REG;
  writeBuffer[1] = OS_ON + analogInput[input] + inputGain + operatingMode;
  write(I2C, writeBuffer, 3);

  writeBuffer[0] = CONV_REG; // indicate that we are ready to read the conversion register    
  write(I2C, writeBuffer, 1);
}

void ads1015WriteConfig(int I2C, int input) {
  // set the pointer to the config register
  writeBuffer[0] = CONFIG_REG;
  writeBuffer[1] = OS_ON + analogInput[input] + inputGain + operatingMode;
  write(I2C, writeBuffer, 3);

  writeBuffer[0] = CONV_REG; // indicate that we are ready to read the conversion register    
  write(I2C, writeBuffer, 1);
}

void mcp23017WriteConfig(int I2C) {
	
  // set the pointer to the config register
  writeBuffer[0] = MCP23017_IODIRA; // GPIO direction register
  writeBuffer[1] = 0xFF; // Set GPIO A to input
  write(I2C, writeBuffer, 2);
  writeBuffer[0] = MCP23017_IODIRB; // GPIO direction register
  writeBuffer[1] = 0xFF; // Set GPIO B to input
  write(I2C, writeBuffer, 2);
  
  writeBuffer[0] = MCP23017_GPPUA; // GPIO Pullup Register
  writeBuffer[1] = 0xFF; // Enable Pullup on GPIO A
  write(I2C, writeBuffer, 2);
  writeBuffer[0] = MCP23017_GPPUB; // GPIO Pullup Register
  writeBuffer[1] = 0xFF; // Enable Pullup on GPIO B
  write(I2C, writeBuffer, 2);
}

void mcp23017_read(int I2C) {
  writeBuffer[0] = MCP23017_GPIOA;
  write(I2C, writeBuffer, 1); //does it autoincrement after a write? i think no. double check its reading the right register after writing the register byte
  read(I2C, mcpReadBuffer, 2); //reading two bytes causes it to autoincrement to the next byte, so it reads port B
}

void readADC(int I2C, int input) {
  read(I2C, readBuffer, 2); // read the conversion. we waited long enough for the reading to be ready, so we arent checking the conversion register
  //int val = readBuffer[0] << 8 | readBuffer[1];
  
  ADCstore[input] = ((readBuffer[0] << 8) | ((readBuffer[1] & 0xff)));
  ADCstore[input] = (ADCstore[input] >> 4) * 3; //bitshift to the right 4 places (see datasheet for reason, and multiply by 3 to get actual voltage)
  //return val;
  //if(1)printf("ADC%d: %d\n", input, val);
}

void ads1015_kill(int I2C) {
  close(I2C);
}

int createUInputDevice() {
  int fd;
  fd = open("/dev/uinput", O_WRONLY | O_NDELAY);
  if (fd < 0) {
    fprintf(stderr, "Can't open uinput device!\n");
    exit(1);
  }
  // device structure
  struct uinput_user_dev uidev;
  memset( & uidev, 0, sizeof(uidev));
  // init event  


	ioctl(fd, UI_SET_EVBIT, EV_KEY);
	ioctl(fd, UI_SET_EVBIT, EV_REL);
	// button
	ioctl(fd, UI_SET_KEYBIT, BTN_A);
	ioctl(fd, UI_SET_KEYBIT, BTN_B);
	ioctl(fd, UI_SET_KEYBIT, BTN_X);
	ioctl(fd, UI_SET_KEYBIT, BTN_Y);
	ioctl(fd, UI_SET_KEYBIT, BTN_TL);
	ioctl(fd, UI_SET_KEYBIT, BTN_TR);
	ioctl(fd, UI_SET_KEYBIT, BTN_SELECT);
	ioctl(fd, UI_SET_KEYBIT, BTN_START);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_UP);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_DOWN);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_LEFT);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_RIGHT);
	ioctl(fd, UI_SET_KEYBIT, BTN_1);
	ioctl(fd, UI_SET_KEYBIT, BTN_2);
	ioctl(fd, UI_SET_KEYBIT, BTN_3);
	ioctl(fd, UI_SET_KEYBIT, BTN_4);
	// axis
	
  ioctl(fd, UI_SET_EVBIT, EV_ABS);
  ioctl(fd, UI_SET_ABSBIT, ABS_X);
  uidev.absmin[ABS_X] = 55; //center position is 127, minimum is near 50
  uidev.absmax[ABS_X] = 200; //center position is 127, maximum is near 200
  uidev.absflat[ABS_X] = 25; //this appears to be the deadzone
  //uidev.absfuzz[ABS_X] = 0; //what does this do?
  ioctl(fd, UI_SET_ABSBIT, ABS_Y);
  uidev.absmin[ABS_Y] = 55; //center position is 127, minimum is near 50
  uidev.absmax[ABS_Y] = 200; //center position is 127, maximum is near 200
  uidev.absflat[ABS_Y] = 25; //this appears to be the deadzone
  //uidev.absfuzz[ABS_Y] = 0; //what does this do?
  snprintf(uidev.name, UINPUT_MAX_NAME_SIZE, "PSPi Controller");
  uidev.id.bustype = BUS_USB;
  uidev.id.vendor = 1;
  uidev.id.product = 5;
  uidev.id.version = 1;
  write(fd, & uidev, sizeof(uidev));
	if(ioctl(fd, UI_DEV_CREATE)) {
		fprintf(stderr, "Error while creating uinput device!\n");
		exit(1);    
	}
  return fd;
}

void sendInputEvent(int fd, uint16_t type, uint16_t code, int32_t value) {
  struct input_event ev;
  memset( & ev, 0, sizeof(ev));
  ev.type = type;
  ev.code = code;
  ev.value = value;
  if (write(fd, & ev, sizeof(ev)) < 0) {
    fprintf(stderr, "1Error while sending event to uinput device!\n");
  }
  // need to send a sync event
  ev.type = EV_SYN;
  ev.code = SYN_REPORT;
  ev.value = 0;
  write(fd, & ev, sizeof(ev));
  if (write(fd, & ev, sizeof(ev)) < 0) {
    fprintf(stderr, "2Error while sending event to uinput device!\n");
  }
}


#define TestBitAndSendKeyEvent(bit, event) sendInputEvent(UInputFIle, EV_KEY, event, 1);



void updateButtons(int UInputFIle, int buttons) {
  // update button event
	sendInputEvent(UInputFIle, EV_KEY, KEY_MUTE, 		!((buttons >> 0x00) & 1));
	sendInputEvent(UInputFIle, EV_KEY, KEY_VOLUMEUP, 	!((buttons >> 0x01) & 1));
	sendInputEvent(UInputFIle, EV_KEY, KEY_VOLUMEDOWN, 	!((buttons >> 0x02) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_TL, 			!((buttons >> 0x03) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_LEFT, 	!((buttons >> 0x04) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_UP, 	!((buttons >> 0x05) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_DOWN, 	!((buttons >> 0x06) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_RIGHT, 	!((buttons >> 0x07) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_TR, 			!((buttons >> 0x08) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_EAST, 		!((buttons >> 0x09) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_NORTH, 		!((buttons >> 0x0A) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_WEST, 		!((buttons >> 0x0B) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_SOUTH, 		!((buttons >> 0x0C) & 1));
	//sendInputEvent(UInputFIle, EV_KEY, HOLD, 			!((buttons >> 0x0D) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_START, 		!((buttons >> 0x0E) & 1));
	sendInputEvent(UInputFIle, EV_KEY, BTN_SELECT, 		!((buttons >> 0x0F) & 1));
	
  uint8_t joystickValue = ADCstore[0]/13; //dividing by 13 to get a center point of 127
    sendInputEvent(UInputFIle, EV_ABS, ABS_X, joystickValue);
	joystickValue = ADCstore[1]/13;
    sendInputEvent(UInputFIle, EV_ABS, ABS_Y, joystickValue);
}

int main(void) {
	int gpio = 11;
	digitalPinMode(gpio, INPUT);
  int adcFile = ads1015_open(); // open ADC I2C device
  int mcpFile = mcp23017_open(); // open Expander device
  ads1015SetConfig(adcFile, 0);
  mcp23017WriteConfig(mcpFile);

  //comment out until everything else is done
  int UInputFIle = createUInputDevice(); // create uinput device
  int ADC = 0;
  
  while (1) {
    //inputSelection = 0xc1;
    //ads1015_read_once(adcFile, 0); //read the ADC

    readADC(adcFile, ADC); //read the ADC
	mcp23017_read(mcpFile); //read the expander
	uint16_t tempReadBuffer = (mcpReadBuffer[0] << 8) | (mcpReadBuffer[1] & 0xff);
	if (tempReadBuffer != previousReadBuffer) {
		if (verbose == 1) {
	printf("Button Mute:%d\n",!((tempReadBuffer >> 0x00) & 1));
	printf("Button Volume+:%d\n",!((tempReadBuffer >> 0x01) & 1));
	printf("Button Volume-:%d\n",!((tempReadBuffer >> 0x02) & 1));
	printf("Button LTrigger:%d\n",!((tempReadBuffer >> 0x03) & 1));
	printf("Button Left:%d\n",!((tempReadBuffer >> 0x04) & 1));
	printf("Button Up:%d\n",!((tempReadBuffer >> 0x05) & 1));
	printf("Button Down:%d\n",!((tempReadBuffer >> 0x06) & 1));
	printf("Button Right:%d\n",!((tempReadBuffer >> 0x07) & 1));
	printf("Button RTrigger:%d\n",!((tempReadBuffer >> 0x08) & 1));
	printf("Button East:%d\n",!((tempReadBuffer >> 0x09) & 1));
	printf("Button North:%d\n",!((tempReadBuffer >> 0x0A) & 1));
	printf("Button West:%d\n",!((tempReadBuffer >> 0x0B) & 1));
	printf("Button South:%d\n",!((tempReadBuffer >> 0x0C) & 1));
	printf("Button Hold Switch:%d\n",!((tempReadBuffer >> 0x0D) & 1));
	printf("Button Start:%d\n",!((tempReadBuffer >> 0x0E) & 1));
	printf("Button Select:%d\n",!((tempReadBuffer >> 0x0F) & 1));
	printf("ADC0:%d ADC1:%d ADC2:%d ADC3:%d\n\n",ADCstore[0]/13,ADCstore[1]/13,ADCstore[2],ADCstore[3]);
		}
	updateButtons(UInputFIle, tempReadBuffer); //only update the joystick when a button is pressed for the time being. will add a check for joystick later
	}
    //ADC = !ADC; //cycle between ADC0 and ADC1. Doesn't currently check battery on ADC2 and ADC3 (only needed every second or so)
	ADC++;
	if (ADC > 3){ ADC = 0;}
    ads1015WriteConfig(adcFile, ADC); //set configuration for ADS1015 for next loop
	//comment out until everything else is done
    
	previousReadBuffer = tempReadBuffer;
    usleep(16666); // sleep for about 1/60th of a second. Also gives the ADC enough time to prepare the next reading
  }
  ads1015_kill(adcFile);
  printf("Cleaning up\n");
  return 0;
}