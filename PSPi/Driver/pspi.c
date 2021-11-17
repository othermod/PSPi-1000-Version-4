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

const int analogInput[] = {
  0x40,
  0x50,
  0x60,
  0x70
}; //Analog Selection for 0/1/2/3

uint8_t readBuffer[2];
uint8_t writeBuffer[3];
uint8_t mcpReadBuffer[2];
uint16_t previousReadBuffer;
uint16_t ADCstore[4];
int verbose = 0;
//this was done on every loop, which isnt needed

bool digitalPinMode(int pin) {
  FILE * fd;
  char fName[128];
  // Exporting the pin to be used
  if ((fd = fopen("/sys/class/gpio/export", "w")) == NULL) {
    printf("Error: unable to export pin\n");
    return false;
  }
  fprintf(fd, "%d\n", pin);
  fclose(fd);
  // Setting direction of the pin
  sprintf(fName, "/sys/class/gpio/gpio%d/direction", pin);
  if ((fd = fopen(fName, "w")) == NULL) {
    printf("Error: can't open pin direction\n");
    return false;
  }
    fprintf(fd, "in\n");
  fclose(fd);
  return true;
}

int digitalRead(int pin) {
  FILE * fd;
  char fName[128];
  char val[2];
  // Open pin value file
  sprintf(fName, "/sys/class/gpio/gpio%d/value", pin);
  if ((fd = fopen(fName, "r")) == NULL) {
    printf("Error: can't open pin value\n");
    return false;
  }
  fgets(val, 2, fd);
  fclose(fd);
  return atoi(val);
}

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

#define DR128 0
#define DR250 0x20
#define DR490 0x40
#define DR920 0x60
#define DR1600 0x80
#define DR2400 0xA0
#define DR3300 0xC0

#define ADS1015_MODE 1 //single shot mode
#define ADS1015_INPUT_GAIN 0 //full 6.144v voltage range
#define ADS1015_COMPARATOR_MODE 0
#define ADS1015_COMPARATOR_POLARITY 0 //active low
#define ADS1015_COMPARATOR_LATCH 0
#define ADS1015_COMPARATOR_QUEUE 0x03 //no comp
#define ADS1015_OS_ON 0x80 // bit 15
// pointer register
#define ADS1015_CONVERT_REGISTER 0
#define ADS1015_CONFIG_REGISTER 1

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

void ads1015SetConfig(int I2C, int input) { //only needs to be done when changing the input
  writeBuffer[1] = ADS1015_OS_ON + analogInput[0] + ADS1015_INPUT_GAIN + ADS1015_MODE;
  if (verbose == 1) printf("writeBuffer[1] : %#x\n", writeBuffer[1]);
  writeBuffer[2] = DR128 + ADS1015_COMPARATOR_MODE + ADS1015_COMPARATOR_POLARITY + ADS1015_COMPARATOR_LATCH + ADS1015_COMPARATOR_QUEUE;
  if (verbose == 1) printf("Setting Configs. writeBuffer[2] : %#x\n", writeBuffer[2]);

  writeBuffer[0] = ADS1015_CONFIG_REGISTER;
  writeBuffer[1] = ADS1015_OS_ON + analogInput[input] + ADS1015_INPUT_GAIN + ADS1015_MODE;
  write(I2C, writeBuffer, 3);

  writeBuffer[0] = ADS1015_CONVERT_REGISTER; // indicate that we are ready to read the conversion register    
  write(I2C, writeBuffer, 1);
}

void ads1015WriteConfig(int I2C, int input) {
  // set the pointer to the config register
  writeBuffer[0] = ADS1015_CONFIG_REGISTER;
  writeBuffer[1] = ADS1015_OS_ON + analogInput[input] + ADS1015_INPUT_GAIN + ADS1015_MODE;
  write(I2C, writeBuffer, 3);

  writeBuffer[0] = ADS1015_CONVERT_REGISTER; // indicate that we are ready to read the conversion register    
  write(I2C, writeBuffer, 1);
}

void readADC(int I2C, int input) {
  read(I2C, readBuffer, 2); // read the conversion. we waited long enough for the reading to be ready, so we arent checking the conversion register
  //int val = readBuffer[0] << 8 | readBuffer[1];

  ADCstore[input] = ((readBuffer[0] << 8) | ((readBuffer[1] & 0xff)));
  ADCstore[input] = (ADCstore[input] >> 4) * 3; //bitshift to the right 4 places (see datasheet for reason, and multiply by 3 to get actual voltage)
  //return val;
  //if(1)printf("ADC%d: %d\n", input, val);
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
  if (ioctl(fd, UI_DEV_CREATE)) {
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
  sendInputEvent(UInputFIle, EV_KEY, KEY_MUTE, !((buttons >> 0x00) & 1));
  sendInputEvent(UInputFIle, EV_KEY, KEY_VOLUMEUP, !((buttons >> 0x01) & 1));
  sendInputEvent(UInputFIle, EV_KEY, KEY_VOLUMEDOWN, !((buttons >> 0x02) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_TL, !((buttons >> 0x03) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_LEFT, !((buttons >> 0x04) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_UP, !((buttons >> 0x05) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_DOWN, !((buttons >> 0x06) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_DPAD_RIGHT, !((buttons >> 0x07) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_TR, !((buttons >> 0x08) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_EAST, !((buttons >> 0x09) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_NORTH, !((buttons >> 0x0A) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_WEST, !((buttons >> 0x0B) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_SOUTH, !((buttons >> 0x0C) & 1));
  //sendInputEvent(UInputFIle, EV_KEY, HOLD, 			!((buttons >> 0x0D) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_START, !((buttons >> 0x0E) & 1));
  sendInputEvent(UInputFIle, EV_KEY, BTN_SELECT, !((buttons >> 0x0F) & 1));

  //disabling joystick for now, will finish that later
  uint8_t joystickValue = ADCstore[0]/13; //dividing by 13 to get a center point of 127
  joystickValue = 127;
  sendInputEvent(UInputFIle, EV_ABS, ABS_X, joystickValue);
  joystickValue = ADCstore[1]/13;
  joystickValue = 127;
  sendInputEvent(UInputFIle, EV_ABS, ABS_Y, joystickValue);
}

int readResolution() {
	FILE *f = fopen("pspi.cfg","r"); // stores horizontal resolution to variable so this works with both LCD types
	char buf[4];
	for (int i = 0 ; i != 0 ; i++) {
    		fgets(buf, 4, f);
	}
	int result;
	fscanf(f, "%d", &result); // would be better to grab it directly, but I'll have to work out the method
	return result;
}

bool isCharging = 0;
bool previousIsCharging = 0;
bool isMute = 1;
bool previousIsMute = 1;
int previousChargeStatus = 99;
int previousIndicationVoltage = 4200;
int chargeStatus = 99;

void updateOSD(int position) {
	previousIsCharging = isCharging;
	if (ADCstore[2] < 500) {isCharging = 1;}
	if (ADCstore[2] > 1000) {isCharging = 0;}
	
	previousChargeStatus = chargeStatus;
	chargeStatus = 0;
	int indicationVoltage = ADCstore[3];
	if (isCharging == 0){
		if (indicationVoltage > 3600) {chargeStatus = 1;}
		if (indicationVoltage > 3638) {chargeStatus = 2;}
		if (indicationVoltage > 3678) {chargeStatus = 3;}
		if (indicationVoltage > 3716) {chargeStatus = 4;}
		if (indicationVoltage > 3748) {chargeStatus = 5;}
		if (indicationVoltage > 3786) {chargeStatus = 6;}
		if (indicationVoltage > 3827) {chargeStatus = 7;}
		if (indicationVoltage > 3873) {chargeStatus = 8;}
		if (indicationVoltage > 3899) {chargeStatus = 9;}
		if (indicationVoltage > 3939) {chargeStatus = 99;}
		if (indicationVoltage > previousIndicationVoltage) {indicationVoltage = previousIndicationVoltage;}
	}
	if (isCharging == 1){
		if (indicationVoltage > 4000) {chargeStatus = 2;}
		if (indicationVoltage > 4023) {chargeStatus = 4;}
		if (indicationVoltage > 4072) {chargeStatus = 7;}
		if (indicationVoltage > 4160) {chargeStatus = 99;}
		if (indicationVoltage < previousIndicationVoltage) {indicationVoltage = previousIndicationVoltage;}
	}
	previousIndicationVoltage = indicationVoltage;
	if ((previousChargeStatus != chargeStatus) || (previousIsCharging != isCharging) || (previousIsMute != isMute)) { // Change Battery Status
		printf("ADC:%d\n",indicationVoltage);
		char temp[512];
		system ("sudo killall pngview 2>/dev/null");
		sprintf(temp, "/home/pi/PSPi/Driver/./pngview -n -b 0 -l 100000 -x %d -y 2 /home/pi/PSPi/Driver/PNG/battery%d%d%d.png &",position - 46,isMute,isCharging,chargeStatus);
		system((char *)temp);
	}
}

int main(void) {
  int resolution = readResolution();
  int gpio = 11;
  digitalPinMode(gpio); //set gpio 11 to input
  int adcFile = ads1015_open(); // open ADC I2C device
  int mcpFile = mcp23017_open(); // open Expander device
  ads1015SetConfig(adcFile, 0);
  mcp23017WriteConfig(mcpFile);

  //comment out until everything else is done
  int UInputFIle = createUInputDevice(); // create uinput device
  int ADC = 0;
  uint8_t sleepADC = 0;
  
  //set initial button condition
  mcp23017_read(mcpFile); 
  uint16_t tempReadBuffer = 0x00;
  updateButtons(UInputFIle, tempReadBuffer);
  
  while (1) {
	  sleepADC++;
	  if (sleepADC == 15) {sleepADC = 0;}
	  if (sleepADC == 0) { //only check ADC every 256 cycles since we are only checking for battery right now
		readADC(adcFile, ADC); //read the ADC
		//printf("ADC%d:%d\n",ADC,ADCstore[ADC]);
		ADC++;
		if (ADC > 3) {ADC = 0;}
		ads1015WriteConfig(adcFile, ADC); //set configuration for ADS1015 for next loop
		updateOSD(resolution);
	  }
	
    mcp23017_read(mcpFile); //read the expander
    tempReadBuffer = (mcpReadBuffer[0] << 8) | (mcpReadBuffer[1] & 0xff);
    if (tempReadBuffer != previousReadBuffer) { 
		updateButtons(UInputFIle, tempReadBuffer); } //only update the controller when a button is pressed for the time being. will add a check for joystick later
    previousReadBuffer = tempReadBuffer;
    usleep(16666); // sleep for about 1/60th of a second. Also gives the ADC enough time to prepare the next reading
  }
  return 0;
}