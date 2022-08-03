create or replace TRIGGER trg_ID_LOGS_ZABBIX
  BEFORE INSERT ON logs_zabbix
  FOR EACH ROW
BEGIN
  SELECT SEQ_ID_LOGS_ZABBIX.nextval
  INTO :new.id
  FROM dual;
END;
