#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#include "control.h"
#include "pointing.h"

int main(int argc, char *argv[]) {
  pthread_t point_loop, control_loop;

  control_init();

  printf("starting threads\n");
  pthread_create(&control_loop, NULL, control_thread, NULL);
  pthread_create(&point_loop, NULL, point_thread, NULL);

  for (;;)
    usleep(1);

  return 0;
}
