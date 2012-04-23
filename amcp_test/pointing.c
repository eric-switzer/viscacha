#include <act_util.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <sys/timeb.h>
#include <time.h>
#include <unistd.h>
#include "control.h"
#include "control_struct.h"
#include "extern.h"
#include "pointing.h"


void *point_thread(void *arg) {
  struct new_point_cmd_t new_point_cmd;

  for (;;) {
    while (!circ_buf_empty(&new_point_cmd_buf)) {
      new_point_cmd = circ_buf_pop(&new_point_cmd_buf, struct new_point_cmd_t);

      if (change_point_info(new_point_cmd.cmd_index, new_point_cmd.val))
        continue;

      printf("point_thread RX: %d\n", new_point_cmd.cmd_index);
    }

    usleep(1);
  }
}

int change_point_info(int ctrl_cmd_index, double val) {
  printf("change_point_info: %d->%10.15g\n", ctrl_cmd_index, val);

  return 1;
}
