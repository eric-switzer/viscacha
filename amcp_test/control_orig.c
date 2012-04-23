#include <act_util.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#include "control.h"
#include "control_struct.h"
#include "extern.h"
#include "pointing.h"

int max_ctrl_cmd_rate;
double *param_val_curr;
double *param_val_new;

int parsecommand(char *cmd, double *cmd_val);

int num_ctrl_cmd_param() {
  static int num = -1;

  if (num < 0)
    for (num = 0; strlen(ctrl_cmd_param[num].name); num++);

  return num;
}

// Find the range of command numbers in the structure.  Note that this is
// different than num_ctrl_cmd_param:  for control of multiple systems,
// there could be several hundred command numbers, but only a subset of those
// that are particular to amcp are in control_struct.c.
int ctrl_cmd_param_max_cmdnum() {
  static int num = -1;
  int i, j;

  if (num < 0) {
    for (i = 0; strlen(ctrl_cmd_param[i].name); i++) {
      j = ctrl_cmd_param[i].cmdnum;
      if (num < j)
        num = j;
    }
  }
  return num;
}

// Find the index of the control param with a given name.
int ctrl_cmd_to_index(const char *field) {
  int i;
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    if (!strcmp(field, ctrl_cmd_param[i].name))
      return i;
  }
  return -1;
}

// Find the index in the ctrl_cmd_param array for a given command number.
int ctrl_cmd_index(int cmdnum) {
  int i;
  static int *mapping = NULL;

  if (mapping == NULL) {
    mapping = (int *)act_malloc("mapping", (ctrl_cmd_param_max_cmdnum() + 1) *
                                           sizeof(int));
    // Unless the command has an entry in ctrl_cmd_param, it gets mapped to -1.
    for (i = 0; i < ctrl_cmd_param_max_cmdnum() + 1; i++)
      mapping[i] = -1;
    for (i = 0; i < num_ctrl_cmd_param(); i++)
      mapping[ctrl_cmd_param[i].cmdnum] = i;
  }

  if (cmdnum < 0 || cmdnum >= num_ctrl_cmd_param())
    return -1;

  return mapping[cmdnum];
}

// Find the number of system types.
int num_ctrl_sys() {
  static int num = -1;

  if (num < 0)
    for (num = 0; strlen(ctrl_sys[num]); num++);

  return num;
}

// Find the system type given the index of ctrl_cmd_param.
int ctrl_cmd_sys(int index) {
  int i, j;
  static int *mapping = NULL;

  if (mapping == NULL) {
    mapping = (int *)act_malloc("mapping", num_ctrl_cmd_param() * sizeof(int));
    for (i = 0; i < num_ctrl_cmd_param(); i++) {
      mapping[i] = -1;
      for (j = 0; j < num_ctrl_sys(); j++) {
        if (!strcmp(ctrl_sys[j], ctrl_cmd_param[i].sys)) {
          mapping[i] = j;
          break;
        }
      }
    }
  }

  return mapping[index];
}

// Checks to see if the command is an input_select type.
char ctrl_cmd_is_select(int ctrl_index) {
  int i;
  static char *mapping = NULL;

  if (mapping == NULL) {
    mapping = (char *)act_malloc("mapping", num_ctrl_cmd_param() *
                                            sizeof(char));
    for (i = 0; i < num_ctrl_cmd_param(); i++) {
      if (!strcmp(ctrl_cmd_param[i].type, CTRL_CMD_SELECT_NAME))
        mapping[i] = 1;
      else
        mapping[i] = 0;
    }
  }

  return mapping[ctrl_index];
}

int parsecommand(char *cmd, double *cmd_val) {
  char *cmd_index, *cmd_value;

  // Get rid of leading white-space.
  for (cmd_index = cmd; *cmd_index == ' ' && *cmd_index != '\0'; cmd_index++);

  // Find the comma.
  if ((cmd_value = strchr(cmd_index, ',')) == NULL) {
    *cmd_val = -1;
    return -1;
  }
  *(cmd_value++) = '\0';

  *cmd_val = atof(cmd_value);

  return atoi(cmd_index);
}

//------------------------------------------------------------------------------
//! Connect to the interface server.
//------------------------------------------------------------------------------

void connect_interface_server() {
  char **identity;
  int i;

  identity = (char **)act_malloc("identity", (num_ctrl_sys() + 1) *
                                             sizeof(char *));
  for (i = 0; i < num_ctrl_sys(); i++)
    identity[i] = strclone(ctrl_sys[i]);
  identity[i] = strclone("");
  ctrl_id = act_interface_client_start("amcp", "amcp", control_version,
                                       (const char **)identity);
}

void control_init() {
  int i, n, cmdnum;
  double cmdval;

  // Allocate the arrays holding the values of the parameter values.
  param_val_curr = (double *)act_malloc("param_val_curr", num_ctrl_cmd_param() *
                                                          sizeof(double));
  param_val_new = (double *)act_malloc("param_val_new", num_ctrl_cmd_param() *
                                                        sizeof(double));

  // Initialise the parameter values to their defaults, in case the interface
  // server can't provide them.
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    param_val_curr[i] = ctrl_cmd_param[i].default_val;
    if (ctrl_cmd_sys(i) == CTRL_SYS_POINTING)
      change_point_info(i, param_val_curr[i]);
  }

  printf("Getting current command values\n");

  while (!act_interface_client_send_msg(ctrl_id, "refresh")) {
    printf("Could not send message \"refresh\" to interface server.\n");
    usleep(1000000);
  }

  for (n = 0;; n++) {
    while (!act_interface_client_msg_avail(ctrl_id))
      usleep(1);
    cmdnum = parsecommand(act_interface_client_get_msg(ctrl_id), &cmdval);

    if (cmdnum < 0) {
      if (cmdval == -1)
        continue;
      else
        break;
    }

    if ((i = ctrl_cmd_index(cmdnum)) < 0)
      break;
    if (i < num_ctrl_cmd_param() && i >= 0)
      param_val_curr[i] = cmdval;
    switch (ctrl_cmd_sys(i)) {
      case CTRL_SYS_POINTING:
        change_point_info(i, cmdval);
        break;
    }
  }
  printf("Finished retrieving %d current command values.\n", n);

  // Set up a circular buffer for giving the pointing system commands.
  circ_buf_init(&new_point_cmd_buf, sizeof(struct new_point_cmd_t),
                NEW_POINT_CMD_BUFLEN);
}

void *control_thread(void *arg) {
  char send_amcp_changes;
  int i, cmdnum, last_frame_pos, frame_pos, memcpy_size;
  double cmdval;
  struct new_point_cmd_t new_point_cmd;
  static int *cmd_change = NULL, *amcp_change = NULL;

  // Allocate the command change registry.  The thread should only be called
  // once, but just to be safe...
  if (cmd_change == NULL)
    cmd_change = (int *)act_calloc("cmd_change", num_ctrl_cmd_param(),
                                   sizeof(int));
  if (amcp_change == NULL)
    amcp_change = (int *)act_calloc("amcp_change", num_ctrl_cmd_param(),
                                    sizeof(int));
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    cmd_change[i] = 0;
    amcp_change[i] = 0;
  }

  // Run control loop at 400 Hz.
  last_frame_pos = 0;
  send_amcp_changes = 0;
  memcpy_size = num_ctrl_cmd_param() * sizeof(double);
  for (;;) {
    frame_pos++;
    if (last_frame_pos != frame_pos) {
      // Check to see if we should register changes amcp made (once per
      // second).
      if (last_frame_pos > frame_pos)
        send_amcp_changes = 1;

      // Make a copy of the current control values to modify.
      memcpy(param_val_new, param_val_curr, memcpy_size);

      for (i = 0; i < num_ctrl_cmd_param(); i++)
        cmd_change[i] = 0;
      while (act_interface_client_msg_avail(ctrl_id)) {
        cmdnum = parsecommand(act_interface_client_get_msg(ctrl_id), &cmdval);
        if ((i = ctrl_cmd_index(cmdnum)) < 0)
          continue;

        // Copy the new parameter value into the modified list and flag it as
        // changed.
        param_val_new[i] = cmdval;
        cmd_change[i] = 1;

        printf("Received command %s with value %g.\n",
                ctrl_cmd_param[i].name, param_val_new[i]);
      }

      // Check to see if anything needs to be updated.
      for (i = 0; i < num_ctrl_cmd_param(); i++) {
        if (param_val_new[i] != param_val_curr[i] && !cmd_change[i])
          amcp_change[i] = 1;

        if (cmd_change[i]) {
          // Push the values of requested change values back to the server.
          act_interface_client_send_msg(ctrl_id,
                                        "controldbput %s reply %f",
                                        ctrl_cmd_param[i].name,
                                        param_val_new[i]);
          printf("Replied to command %s with value %g.\n",
                          ctrl_cmd_param[i].name, param_val_new[i]);

          if (amcp_change[i])
            amcp_change[i] = 0;
        }
        else if (amcp_change[i] && send_amcp_changes) {
          // Every second (when send_amcp_changes = 1), send any changes not
          // requested by the interface_server, but which have been changed by
          // amcp (e.g., during autocycling).
          act_interface_client_send_msg(ctrl_id,
                                        "controldbput %s reply %f",
                                        ctrl_cmd_param[i].name,
                                        param_val_new[i]);

          amcp_change[i] = 0;
        }

        // Only implement a command if its value changed, or if it was a
        // simple push-button request.
        if (param_val_new[i] == param_val_curr[i] &&
            !(ctrl_cmd_is_select(i) && cmd_change[i]))
          continue;

        switch (ctrl_cmd_sys(i)) {
          case CTRL_SYS_POINTING:
            new_point_cmd.cmd_index = i;
            new_point_cmd.val = param_val_new[i];
            if (!circ_buf_full(&new_point_cmd_buf))
              circ_buf_push(&new_point_cmd_buf, new_point_cmd);
            else
              printf("Circular buffer for new_point_cmd full.\n");
            break;
        }
      }

      // The new values become the current values.
      memcpy(param_val_curr, param_val_new, memcpy_size);
      last_frame_pos = frame_pos;
      send_amcp_changes = 0;
    }
    else
      usleep(1);
  }

  return NULL;
}
