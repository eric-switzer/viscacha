#ifndef EXTERN_H
#define EXTERN_H

// This file is simply a list of variables declared in *_struct.c files.
// Because they are initialised when they are declared, they can't appear in
// headers.  Hence the need for this list of externs, collected in this file so
// they don't clutter up other files.

// From control_struct.c
#include "control.h"
extern char ctrl_sys[][16];
extern struct ctrl_cmd_param_t ctrl_cmd_param[];

#endif
