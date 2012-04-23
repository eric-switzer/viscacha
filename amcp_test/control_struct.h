#ifndef CONTROL_STRUCT_H
#define CONTROL_STRUCT_H

extern const char control_version[];

enum ctrl_sys_type_t {
  CTRL_SYS_POINTING,
  CTRL_SYS_KUKA_DN,
  CTRL_SYS_INT_VARIABLE,
  CTRL_SYS_ABOB,
  CTRL_SYS_SNYC,
  CTRL_SYS_BBC,
  CTRL_SYS_END_OF_ENUM
};

enum map_multi_t {
  map_multi_end_of_enum
};

enum ctrl_cmd_param_idx_t {
  window_close_idx,
  point_mv_accel_idx,
  dn_pgno_valid_idx,
  dn_conf_mess_idx,
  dn_stop_scan_idx,
  point_az_idx,
  dn_imm_stop_idx,
  point_sec_mir_t_idx,
  point_sec_fr_l_idx,
  point_sec_mir_r_idx,
  dn_newmsgack_idx,
  dn_krdltrigger_idx,
  point_scan_plus_idx,
  dn_ext_start_idx,
  dn_var_1_rdy_idx,
  point_scan_minus_idx,
  dn_recover_idx,
  point_go_azel_idx,
  dn_extend_pins_idx,
  point_scan_num_idx,
  dn_reset_all_idx,
  dn_drives_off_idx,
  snyc_framerate_idx,
  point_stop_motion_idx,
  snyc_numrows_idx,
  point_sec_fr_r_idx,
  point_go_stow_idx,
  dn_i_o_act_idx,
  point_move_sec_zero_idx,
  point_scan_accel_idx,
  window_pow_idx,
  dn_heartbeat_enable_idx,
  dn_retract_pins_idx,
  window_open_idx,
  dn_drives_on_idx,
  point_sec_mir_l_idx,
  dn_down_seq_idx,
  window_pol2_idx,
  window_pol1_idx,
  dn_var_2_rdy_idx,
  snyc_manchout_idx,
  point_move_sec_idx,
  point_poll_motion_idx,
  point_scan_start_idx,
  dn_prog_parity_idx,
  point_do_warm_idx,
  point_mv_speed_idx,
  point_el_idx,
  dn_start_seq_idx,
  snyc_framenum_idx,
  point_track_start_idx,
  snyc_rowlen_idx,
  point_go_maint_idx,
  point_go_home_idx,
  point_scan_secs_idx,
  point_scan_speed_idx,
  ctrl_sys_param_idx_end_of_enum
};

#endif
