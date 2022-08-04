import os
import time
# from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MONITOR_PATH_INPUT = "C:\\apicifrado\\DecodeEntrada"
MONITOR_PATH_OUTPUT = "C:\\apicifrado\\DecodeSalida"


class Watcher:

    def run(self):
        w = Observer()
        w.schedule(Handler(), MONITOR_PATH_INPUT, recursive=True)
        w.start()
        try:
            while True:
                time.sleep(5)
        except:
            w.stop()
            print("Error")

        w.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print(event.event_type)

        if event.is_directory:
            return None

        elif event.event_type == 'created':
            print(f"File created {event.src_path}")

        elif event.event_type == 'modified':
            # filename = f"tran{datetime.now().strftime('%Y%m%d%H%M%S_%f')}.txt"
            filename = os.path.basename(event.src_path)
            APICIFRADODECODE = "C:\\apicifrado\\CmpApiCifradoDecode.bat"
            cmd = f"{APICIFRADODECODE} {event.src_path} {MONITOR_PATH_OUTPUT}\\{filename}"
            print(cmd)
            os.system(cmd)


Watcher().run()
