CC          = gcc -c
LINK        = gcc
CCFLAGS     = -O2 -Wall -std=gnu99 -Iinclude/
PREFIX      = /usr/sbin
INITD_LOC   = /etc/init.d
TARGET      = amcp
TARGETC     = amcp.c
INITD       = amcp
DOCFILE     = amcp.doc
LDFLAGS	   = -lpthread -lm -lact_util -levent -lhiredis -Llib/
AMCP_FLAGS =
HEADERS	   = control.h control_struct.h pointing.h
OBJS       = control.o control_struct.o pointing.o

  
all: $(TARGET)
	
$(TARGET): $(TARGETC) $(OBJS) $(HEADERS) Makefile $(LIB) 
	$(LINK) $(CCFLAGS) $(AMCP_FLAGS) -o $(TARGET) $(TARGETC) $(OBJS) $(LDFLAGS)
	
%.o: %.c $(HEADERS) Makefile
	$(CC) $(CCFLAGS) $(AMCP_FLAGS) -c $<

.PHONY: clean
clean:
	-rm -f *~ $(OBJS) $(TARGET)
