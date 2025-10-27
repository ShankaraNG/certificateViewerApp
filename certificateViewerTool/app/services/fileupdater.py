import services.datacollector as datacollector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logger as logging


def update_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact):
    try:
        # Read all lines
        with open(file_path, 'r') as file:
            lines = file.readlines()
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Update Operation has been started")
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Reading the backend file")
        header = lines[0]  # Preserve header
        updated_lines = [header]

        found = False
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Searching for the backend entry")
        # Iterate over remaining lines
        for line in lines[1:]:
            system, host, port, team_email, manager_email, emergency_contact = line.strip().split("|")

            # If host and port match — replace line
            if host == target_host and port == target_port and target_system == system:
                new_entry = f'{system}|{host}|{port}|{target_team_email}|{target_manager_email}|{target_contact}'
                updated_lines.append(new_entry + '\n')
                found = True
            else:
                updated_lines.append(line)

        if not found:
            logging.logger('INFO', 'Certificate Viewer Tool', 200, f"No matching entry for Host: {target_host} and Port: {target_port}")
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Update Process has been completed')
            return False
        else:
            # Write back the updated content
            with open(file_path, 'w') as file:
                file.writelines(updated_lines)
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Match has been found')
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'File has been updated successfully')
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Refreshing the certificate data')
            datacollector.certificateDataCollector()
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Refreshing of the certificate data has been completed')
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Update Process has been completed')
            return True
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

# Example usage
# file_path = 'C:\\Users\\shankara.nanjangudga\\Desktop\\pythonscript\\certificatewebsite\\backend_systems.lst'
# target_host = 'apple.com'
# target_port = '443'
# target_system = 'apple'
# target_team_email = 'newteam@gmail.com'
# target_manager_email = 'newmanager@gmail.com'
# target_contact = '1234567890'

# update_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact)
