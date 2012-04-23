#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <hiredis/hiredis.h>
#include <hiredis/async.h>
#include <hiredis/adapters/libevent.h>
#include "uthash.h"
#define CTRL_KEY_LEN 256

typedef struct ctrl_entry_t {
    char key[CTRL_KEY_LEN];
    double min;
    double max;
    double param_val;
    UT_hash_handle hh;
} ctrl_entry_t;

ctrl_entry_t *ctrl_entires=NULL, *ctrl_entry;

double get_ctrl(const char *name) {
    HASH_FIND_STR(ctrl_entires, name, ctrl_entry);
    if (ctrl_entry) {
        printf("found %s (param_val %10.15g)\n", ctrl_entry->key, ctrl_entry->param_val);
    } else {
        printf("failed to find %s\n", name);
    }
    return ctrl_entry->param_val;
}

int init_ctrl(void) {
    char str[CTRL_KEY_LEN];
    double min, max, def;
    FILE *fp_ctrl_file;

    fp_ctrl_file = fopen ("myfile.txt","r");
    while (fscanf(fp_ctrl_file, "%s %lf %lf %lf", str, &min, &max, &def) != EOF) {
        printf("%s min=%g max=%g default=%g\n", str, min, max, def);
        if ( (ctrl_entry = (ctrl_entry_t*)malloc(sizeof(ctrl_entry_t))) == NULL) exit(-1);
        strncpy(ctrl_entry->key, str, CTRL_KEY_LEN);
        ctrl_entry->min = min;
        ctrl_entry->max = max;
        ctrl_entry->param_val = def;
        HASH_ADD_STR(ctrl_entires, key, ctrl_entry);
    }
    fclose(fp_ctrl_file);

    return 0;
}

void onMessage(redisAsyncContext *c, void *reply, void *privdata) {
    redisReply *r = reply;
    int j;
    if (reply == NULL) return;

    if (r->type == REDIS_REPLY_ARRAY) {
        for (j = 0; j < r->elements; j++) {
            printf("%u) %s\n", j, r->element[j]->str);
        }
    }
}

int main (int argc, char **argv) {
    init_ctrl();
    get_ctrl("this_is_a_name");
    get_ctrl("this_is_b_name");
    get_ctrl("this_is_c_name");

    signal(SIGPIPE, SIG_IGN);
    struct event_base *base = event_base_new();

    redisAsyncContext *c = redisAsyncConnect("127.0.0.1", 6379);
    if (c->err) {
        printf("error: %s\n", c->errstr);
        return 1;
    }

    redisLibeventAttach(c, base);
    redisAsyncCommand(c, onMessage, NULL, "SUBSCRIBE testtopic");
    event_base_dispatch(base);
    return 0;
}
