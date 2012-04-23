/*
Alterations:
needed to define UNITS_LEN and FIELD_LEN locally
*/
#ifndef CONTROL_H
#define CONTROL_H

#include <act_util.h>
//#include <act_spec.h>

//#include "io.h"

#define CTRL_CMD_TYPE_LEN           32
#define CTRL_CMD_SYS_LEN            32
#define UNITS_LEN                   32
#define FIELD_LEN                   256
struct ctrl_cmd_param_t {
  char name[FIELD_LEN];
  char type[CTRL_CMD_TYPE_LEN];
  char sys[CTRL_CMD_SYS_LEN];
  char units[UNITS_LEN];
  double min;
  double max;
  double default_val;
  int cmdnum;
};
#define END_OF_CTRL_CMD_PARAM       {"", "", "", "", -1, -1, -1, -1}
#define END_OF_CTRL_SYS             ""

#define CTRL_CMD_SELECT_NAME        "input_select"

#define NEW_POINT_CMD_BUFLEN        256
struct new_point_cmd_t {
  int cmd_index;
  double val;
};
struct circ_buf_t new_point_cmd_buf;
int ctrl_id;      //!< The ID for the interface client.

void connect_interface_server();
void control_init();
void write_ctrl_cmd_vals(int pos, int page);
void *command_thread(void *arg);
void *control_thread(void *arg);
char ctrl_cmd_is_select(int ctrl_index);
int num_ctrl_cmd_param();
int ctrl_cmd_param_max_cmdnum();
int ctrl_cmd_name_to_index(const char *field);
int ctrl_cmd_index(int cmdnum);
int num_ctrl_sys();
int ctrl_cmd_sys(int index);
int ctrl_cmd_to_bbcio_write_map(int ctrl_index);
int ctrl_cmd_to_bbcio_write_val(int ctrl_index);
int ctrl_cmd_to_sensorayio_write_map(int ctrl_index);
int ctrl_cmd_to_kuka_dn_write_map(int ctrl_index);

#endif
