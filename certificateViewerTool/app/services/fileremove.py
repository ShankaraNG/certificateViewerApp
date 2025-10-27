import services.datacollector as datacollector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logger as logging

def remove_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact):
    try:
        # Read all lines
        with open(file_path, 'r') as file:
            lines = file.readlines()
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Remove Operation has been started")
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Reading the existing entry file")
        header = lines[0]  # Preserve header
        updated_lines = [header]

        found = False
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Checking if the entry exists in the backend")
        # Iterate over remaining lines
        for line in lines[1:]:
            system, host, port, team_email, manager_email, emergency_contact = line.strip().split("|")

            # If host and port match — replace line
            if host == target_host and port == target_port and target_system == system:
                found = True
                continue
            else:
                updated_lines.append(line if line.endswith('\n') else line + '\n')

        if not found:
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "No Match found")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "certificate entry doesnt exists")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Remove Operation has been completed')
            return "Entry doesnt exists"
        else:
            with open(file_path, 'w') as file:
                file.writelines(updated_lines)
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "certificate entry has been found")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "certificate entry has been deleted")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "refreshing the certificate data")
            datacollector.certificateDataCollector()
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "Refresh has been completed")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "Remove Operation has been completed")
            return "Entry has been Deleted."
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

# # Example usage
# file_path = 'C:\\Users\\shankara.nanjangudga\\Desktop\\pythonscript\\certificatewebsite\\backend_systems.lst'
# target_host = 'apple.com'
# target_port = '443'
# target_system = 'apple'
# target_team_email = 'newteam@gmail.com'
# target_manager_email = 'newmanager@gmail.com'
# target_contact = '1234567890'

# remove_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact)
