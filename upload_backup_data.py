from datetime import datetime
import os
import upload_backup_data_config


class Upload_Backup():
    """
    upload backup data

    slow as record per command, but handy
    """

    def __init__(self,
                 config,
                 csv_backup_file):
        """init + config"""

        self.config = config
        
        self.debug_cmd = self.config.FLAG_DEBUG_CMD
        
        self.influx_bucket = self.config.INFLUX_BUCKET
        self.influx_write = self.config.FLAG_INFLUX_WRITE
    
        with open(csv_backup_file, 'r') as f:
            self.backup_data_file=f.readlines()

        print('{}\n{} records\ninflux_bucket: {}\ninflux_write: {}\n'.format(datetime.now(),
                                                                             len(self.backup_data_file),
                                                                             self.influx_bucket,
                                                                             self.influx_write))
            

    def import_data(self):
            """
            #HEADER
            measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts

            #DATA
            dallas,ruth,mrazak,96928329000,14,labjack,true,20.1875,1635721207221
            dallas,ruth,mrazak,910462155048,14,labjack,true,20.375,1635721208091
            dallas,ruth,mrazak,1052176647976,14,labjack,true,20.3125,1635721208962            

            ts/timestamp -> ms precision
            """

            for f in self.backup_data_file:
                measurement, host, machine_id, ds_id, ds_carrier, ds_valid, ds_pin, ds_decimal, ts=f.strip().split(',')     

                cmd_run=self.config.TEMPLATE_CURL.format(
                    secure=self.config.INFLUX_SECURE,
                    server=self.config.INFLUX_SERVER,
                    port=self.config.INFLUX_PORT,
                    org=self.config.INFLUX_ORG,
                    precision=self.config.INFLUX_PRECISION, # ms
                    token=self.config.INFLUX_TOKEN,
                    
                    bucket=self.influx_bucket,
                
                    measurement=measurement,
                    host=host,

                    machine_id=machine_id,
                    ds_id=ds_id,
                    ds_carrier=ds_carrier,
                    ds_valid=ds_valid,
                    ds_pin=ds_pin,
                    ds_decimal=ds_decimal,

                    ts=ts) # 1234567890123

                if self.influx_write:
                    ooo=os.system(cmd_run)
        
                if self.debug_cmd:
                    print('{}\n'.format(cmd_run.replace(self.config.INFLUX_TOKEN,
                                                        '...')))


    def flux_explore(self):
        """flux debug cmd"""

        flux_debug_cmd = '''
        from(bucket: "{bucket}") 
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop) 
        |> filter(fn: (r) => r["_measurement"] == "dallas") 
        
        //|> filter(fn: (r) => r["DsId"] != "236134354984")  
    
        //|> drop(columns: ["_start", "_stop", "_measurement", "DsValid"]) 
        
        //|> sort(columns: ["_time"], desc:true)  

        |> yield(name: "min")
        '''.format(bucket=self.influx_bucket)

        print(flux_debug_cmd)


#GLOBAL
def push_config_csv():
    """upload csv file specified in config"""

    upload_backup = Upload_Backup(config=upload_backup_data_config,
                                  csv_backup_file=upload_backup_data_config.CSV_BACKUP_FILE)

    upload_backup.import_data()


def push_files(filenames, work_dir):
    """upload more backup files in one go"""

    for single_file in filenames:
        full_path = os.path.join(work_dir,
                                 single_file)

        upload_backup = Upload_Backup(config=upload_backup_data_config,
                                      csv_backup_file=full_path)

        upload_backup.import_data()

 
if __name__ == "__main__":
    """$python3 upload_backup_data.py 1>1_debug_upload_backup_data.log 2>2_debug_upload_backup_data.log"""

    #SINGLE CSV FILE DEFINED IN CONFIG
    #"""
    push_config_csv()
    #"""

    #FILES ARE IN SAME DIR
    """
    push_files(filenames=['2021_10_26_ds_sensor_14.csv',
                          '2021_10_27_ds_sensor_14.csv',
                          '2021_10_28_ds_sensor_14.csv'],
               work_dir='/home/conan/soft/labjack_switch_board/csv/')
    """
