#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import logging
import pymysql
import ConfigParser


class MysqlTool:
    def Backup(self):
        cf = ConfigParser.ConfigParser()
        cf.read("./conf/config.ini")
        self.host     = cf.get("mysql", "host")
        self.port     = cf.getint("mysql", "port")
        self.username = cf.get("mysql", "username")
        self.password = cf.get("mysql", "password")

        DATETIME = time.strftime('%Y%m%d-%H%M%S')
        BACKUP_PATH = "/backup/"
        BACKUP_FILE = BACKUP_PATH + 'orchestration-' + DATETIME  + '.sql'

        mysql_cmd = "mysqldump -h %s -P %d -u %s -p%s %s > %s" % \
              (self.host, self.port, self.username, self.password,
               'orchestration', BACKUP_FILE)
        print mysql_cmd
        os.system(mysql_cmd)


class DBHelper:

    def __init__(self, database):

        cf = ConfigParser.ConfigParser()
        cf.read("./conf/config.ini")
        self.host     = cf.get("mysql", "host")
        self.port     = cf.getint("mysql", "port")
        self.username = cf.get("mysql", "username")
        self.password = cf.get("mysql", "password")

        self.database = database


    def Connect(self):
        self.db = pymysql.connect(       host=self.host,
                                    port=self.port,
                                    user=self.username,
                                    password=self.password,
                                    db=self.database,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def Close(self):
        self.cursor.close()
        self.db.close()

    def GetBluePrintUUIDs(self):
        self.cursor.execute("SELECT uuid from blue_print")
        return [rec['uuid'] for rec in self.cursor.fetchall()]

    def GetBluePrint(self, uuid):
        self.cursor.execute("SELECT template from blue_print where uuid='%s'" % uuid)
        data =  self.cursor.fetchone()
        return data['template']

    def UpdateBluePrint(self, uuid, yaml_stream):
        #self.cursor.execute("UPDATE blue_print set template='%s' where uuid='%s'" %(yaml_stream, uuid))
        logging.WARN("UPDATE blue_print set template='%s' where uuid='%s'" %(yaml_stream, uuid))

    def GetStackUUIDs(self):
        self.cursor.execute("SELECT uuid from tosca_stack")
        return [rec['uuid'] for rec in self.cursor.fetchall()]

    def GetStackTemplate(self, uuid):
        self.cursor.execute("SELECT template from tosca_stack where uuid='%s'" % uuid)
        data =  self.cursor.fetchone()
        return data['template']

    def UpdateStackTemplate(self, uuid, yaml_stream):
        #self.cursor.execute("UPDATE tosca_stack set template='%s' where uuid='%s'" % (yaml_stream, uuid))
        logging.WARN("UPDATE tosca_stack set template='%s' where uuid='%s'" % (yaml_stream, uuid))


def DisplayUUIDs(uuids):
    logging.info("template uuids:")
    for uuid in uuids:
        logging.info("  %s" % uuid)


def ProcessDockerVolume(uuid, old_stream):
    if not old_stream:
        return None

    from yaml import load, dump

    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    data = load(old_stream)
    need_update = False
    for key, value in data['topology_template']['node_templates'].items():
        if value['type'] != 'tosca.nodes.wise2c.DockerVolume':
            continue

        if not value['properties'].has_key('driver'):
            continue

        if value['properties']['driver'] == '':
            continue

        if not isinstance(value['properties']['driver'], dict):
            continue

        if not value['properties']['driver'].has_key('get_input'):
            continue

        data['topology_template']['node_templates'][key]['properties']['host_path'] = value['properties']['driver']
        data['topology_template']['node_templates'][key]['properties']['driver']    = ''

        need_update = True


    if need_update:
        new_stream = dump(data)
        logging.info("uuid: %s" % uuid)
        logging.info("\nold: %s" % old_stream)
        logging.info("\nnew: %s" % new_stream)
        return new_stream
    return None

def init_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  #


def main():
    init_logger()
    logging.info("setup 1. backup the database orchestration.")
    try:
        tool = MysqlTool()
        tool.Backup()
    except Exception as e:
        logging.error('backup the orchestration is error. %s' % e)


    logging.info("setup 2. update the blueprint")
    try:
        db_helper = DBHelper('orchestration')
        db_helper.Connect()
        logging.info('connect orchestration database is ok.')

        uuids = db_helper.GetBluePrintUUIDs()
        DisplayUUIDs(uuids)
        for uuid in uuids:
            old_stream = db_helper.GetBluePrint(uuid)
            new_stream = ProcessDockerVolume(uuid, old_stream)
            if new_stream != None:
                db_helper.UpdateBluePrint(uuid, new_stream)
        logging.info('the orchestration database upgrade is successed.')

        db_helper.Close()
    except Exception as e:
        logging.error('upgrade the blueprint is error. %s' % e)


    logging.info("setup 3. update the tosca_stack")
    try:
        db_helper = DBHelper('orchestration')
        db_helper.Connect()
        logging.info('connect orchestration database is ok.')

        uuids = db_helper.GetStackUUIDs()
        DisplayUUIDs(uuids)
        for uuid in uuids:
            old_stream = db_helper.GetBluePrint(uuid)
            new_stream = ProcessDockerVolume(uuid, old_stream)
            if new_stream != None:
                db_helper.UpdateStackTemplate(uuid, new_stream)
        logging.info('the orchestration database upgrade is successed.')

        db_helper.Close()
    except Exception as e:
        logging.error('upgrade the tosca_stack is error. %s' % e)

if __name__ == "__main__":
    main()