#include <act_util.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <sys/types.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <hiredis/hiredis.h>
#include <hiredis/async.h>
#include <hiredis/adapters/libevent.h>

#include "control.h"
#include "control_struct.h"
#include "extern.h"
#include "pointing.h"

#define REDIS_HOST "127.0.0.1"
#define REDIS_HOST_PORT 6379
#define REDIS_HK_CHANNEL "housekeeping"
#define REDIS_HK_ACK_CHANNEL "housekeeping_ack"

int max_ctrl_cmd_rate;
double *param_val_curr;
// flag: external command received or amcp request
int *cmd_change, *amcp_change;

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

void control_init() {
  pthread_t command_loop;
  redisContext *redis;
  redisReply *reply;
  int i;
  int push_default = 0;

  // Allocate the arrays holding the values of the parameter values.
  param_val_curr = (double *)act_malloc("param_val_curr", num_ctrl_cmd_param() *
                                                          sizeof(double));
  if (cmd_change == NULL)
    cmd_change = (int *)act_calloc("cmd_change", num_ctrl_cmd_param(),
                                   sizeof(int));
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    cmd_change[i] = 0;
  }
  if (amcp_change == NULL)
    amcp_change = (int *)act_calloc("amcp_change", num_ctrl_cmd_param(),
                                    sizeof(int));
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    amcp_change[i] = 0;
  }

  // set parameters to safe defaults in case redis fails
  for (i = 0; i < num_ctrl_cmd_param(); i++) {
    param_val_curr[i] = ctrl_cmd_param[i].default_val;
    if (ctrl_cmd_sys(i) == CTRL_SYS_POINTING)
      change_point_info(i, param_val_curr[i]);
  }

  printf("Getting current command values\n");

  redis = redisConnect(REDIS_HOST, REDIS_HOST_PORT);
  if(redis->err) {
    fprintf(stderr, "Connection error: %s\n", redis->errstr);
    exit(EXIT_FAILURE);
  }

  if (push_default) {
    for (i = 0; i < num_ctrl_cmd_param(); i++) {
      reply = redisCommand(redis, "SET %s %10.15g",
                           ctrl_cmd_param[i].name,
                           ctrl_cmd_param[i].default_val);
      freeReplyObject(reply);

      printf("SET %s %10.15g: %s\n",
             ctrl_cmd_param[i].name,
             ctrl_cmd_param[i].default_val,
             reply->str);

    }
  } else {
    for (i = 0; i < num_ctrl_cmd_param(); i++) {
      reply = redisCommand(redis, "GET %s", ctrl_cmd_param[i].name);
      if ( reply->type == REDIS_REPLY_ERROR ) {
        printf( "Error: %s\n", reply->str );
      } else if ( reply->type != REDIS_REPLY_STRING ) {
        printf( "Unexpected type: %d\n", reply->type );
      } else {
        sscanf( reply->str, "%lf", &param_val_curr[i]);
        printf( "Result for %s: %10.15g\n",
                ctrl_cmd_param[i].name,
                param_val_curr[i]);
      }
      freeReplyObject(reply);
    }
    // DO WE NEED OTHER HANDLERS HERE?
  }

  // Set up a circular buffer for giving the pointing system commands.
  circ_buf_init(&new_point_cmd_buf, sizeof(struct new_point_cmd_t),
                NEW_POINT_CMD_BUFLEN);

  printf("Starting command thread\n");
  pthread_create(&command_loop, NULL, command_thread, NULL);
}

void message_handler(redisAsyncContext *c, void *reply, void *privdata) {
  redisReply *r = reply;
  int cmdindex;
  double cmdval;
  char *sp;

  if (reply == NULL) return;

  if (r->type == REDIS_REPLY_ARRAY) {
    if (!strcmp(r->element[1]->str, REDIS_HK_CHANNEL)) {
      if( r->element[2]->str != NULL ) {
        sp = strchr(r->element[2]->str, ' ');
        if(sp != NULL) {
          *sp++ = '\0';
          sscanf( sp, "%lf", &cmdval);
          cmdindex = ctrl_cmd_to_index(r->element[2]->str);
          if (cmdindex > 0) {
            param_val_curr[cmdindex] = cmdval;
            cmd_change[cmdindex] = 1;
            printf("Received command %s (idx=%d) with value %g.\n",
                    ctrl_cmd_param[cmdindex].name,
                    cmdindex,
                    param_val_curr[cmdindex]);
          } else {
            printf("Unknown system variable received: %s\n", r->element[2]->str);
          }
        } else {
          printf("Malformed command received: %s\n", r->element[2]->str);
        }
      }
    }
    if (!strcmp(r->element[1]->str, "messages")) {
      printf("received a message");
    }
  }

  return;
}

void *command_thread(void *arg) {
  signal(SIGPIPE, SIG_IGN);
  struct event_base *base = event_base_new();

  redisAsyncContext *c = redisAsyncConnect(REDIS_HOST, REDIS_HOST_PORT);
  if (c->err) {
    printf("REDIS not connected: %s\n", c->errstr);
  }

  redisLibeventAttach(c, base);
  redisAsyncCommand(c, message_handler, NULL, "SUBSCRIBE housekeeping");
  event_base_dispatch(base);
  return 0;
}

void *control_thread(void *arg) {
  char send_amcp_changes;
  int i, last_frame_pos;
  int frame_pos = 0;  // FOR TESTING ONLY
  struct new_point_cmd_t new_point_cmd;
  redisContext *redis;
  redisReply *reply;

  redis = redisConnect(REDIS_HOST, REDIS_HOST_PORT);
  if(redis->err) {
    fprintf(stderr, "Connection error: %s\n", redis->errstr);
    exit(EXIT_FAILURE);
  }

  // Run control loop at 400 Hz.
  last_frame_pos = 0;
  send_amcp_changes = 0;
  for (;;) {
    frame_pos++;
    if (last_frame_pos != frame_pos) {
      // Check to see if we should register changes amcp made (once per
      // second).
      if (last_frame_pos > frame_pos)
        send_amcp_changes = 1;

      // Check to see if anything needs to be updated.
      for (i = 0; i < num_ctrl_cmd_param(); i++) {
        if (cmd_change[i]) {
          // Push the values of requested change values back to the server.
          reply = redisCommand(redis, "SET %s %10.15g",
                               ctrl_cmd_param[i].name,
                               param_val_curr[i]);
          freeReplyObject(reply);

          reply = redisCommand(redis, "PUBLISH %s %s",
                               REDIS_HK_ACK_CHANNEL,
                               ctrl_cmd_param[i].name);
          freeReplyObject(reply);

          printf("Ack: %s->%g.\n",
                 ctrl_cmd_param[i].name, param_val_curr[i]);

          // reset and also block a change by amcp if made at the same time
          cmd_change[i] = 0;
          if (amcp_change[i]) {
            amcp_change[i] = 0;
          }
        } else if (amcp_change[i] && send_amcp_changes) {
          // Every second (when send_amcp_changes = 1), send any changes not
          // requested by the interface_server, but which have been changed by
          // amcp (e.g., during autocycling).
          reply = redisCommand(redis, "SET %s %10.15g",
                               ctrl_cmd_param[i].name,
                               param_val_curr[i]);
          freeReplyObject(reply);

          reply = redisCommand(redis, "PUBLISH %s %s",
                               REDIS_HK_ACK_CHANNEL,
                               ctrl_cmd_param[i].name);
          freeReplyObject(reply);

          printf("AMCP pushed %s->%g.\n",
                 ctrl_cmd_param[i].name, param_val_curr[i]);

          amcp_change[i] = 0;
        }

        // Only implement a command if its value changed, or if it was a
        // simple push-button request.
        if (!ctrl_cmd_is_select(i) || !cmd_change[i] || !amcp_change[i])
          continue;

        switch (ctrl_cmd_sys(i)) {
          case CTRL_SYS_POINTING:
            new_point_cmd.cmd_index = i;
            new_point_cmd.val = param_val_curr[i];
            if (!circ_buf_full(&new_point_cmd_buf))
              circ_buf_push(&new_point_cmd_buf, new_point_cmd);
            else
              printf("Circular buffer for new_point_cmd full.\n");
            break;
        }
      }

      last_frame_pos = frame_pos;
      send_amcp_changes = 0;
      usleep(100000);
    } else {
      usleep(1);
    }
  }

  return NULL;
}
