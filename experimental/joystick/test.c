#include <linux/input.h>
#include <linux/uinput.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

int main () {
	int fd;
	fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
	if (fd < 0) {
		fprintf(stderr, "Failed to open!\n");
		exit(EXIT_FAILURE);
	}
	printf("Opened uinput\n");

	close(fd);
}
