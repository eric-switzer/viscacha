SRC_DIR     = /usr/src/python/interface_server/
BIN_DIR     = /usr/sbin/
CONFIG_LOC  = /etc/
INITD_LOC   = /etc/init.d/

install:
	install -d $(SRC_DIR)
	install -m 644 interface_server.py $(SRC_DIR)
	install -m 644 amcp_interface.py $(SRC_DIR)
	install -m 644 mce_interface.py $(SRC_DIR)
	install -m 644 generic_interface.py $(SRC_DIR)
	install -m 644 command_interface.py $(SRC_DIR)
	install -m 644 login_interface.py $(SRC_DIR)
	install -m 644 interfaces.py $(SRC_DIR)
	install -m 644 param.py $(SRC_DIR)
	install -m 644 user_interface.py $(SRC_DIR)
	install -m 644 control_parse.py $(SRC_DIR)
	install -m 644 daemonize.py $(SRC_DIR)
	install -m 644 logger.py $(SRC_DIR)
	install -m 755 call_interface_server $(BIN_DIR)
	install -m 644 interface_server.conf $(CONFIG_LOC)
	install -m 755 interface_server $(INITD_LOC)
	/sbin/chkconfig --add interface_server
	$(INITD_LOC)/interface_server restart

uninstall:
	$(INITD_LOC)/interface_server stop
	rm -f $(SRC_DIR)/interface_server.py
	rm -f $(SRC_DIR)/control_parse.py
	rm -f $(SRC_DIR)/daemonize.py
	rm -f $(SRC_DIR)/logger.py
	rm -f $(SRC_DIR)/param.py
	rm -f $(SRC_DIR)/command_interface.py
	rm -f $(SRC_DIR)/login_interface.py
	rm -f $(SRC_DIR)/interfaces.py
	rm -f $(SRC_DIR)/user_interface.py
	rm -f $(SRC_DIR)/amcp_interface.py
	rm -f $(SRC_DIR)/mce_interface.py
	rm -f $(SRC_DIR)/generic_interface.py
	rm -f $(BIN_DIR)/call_interface_server
	rm -f $(CONFIG_LOC)/interface_server.conf
	rm -f $(INITD_LOC)/interface_server
