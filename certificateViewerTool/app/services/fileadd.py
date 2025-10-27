import services.datacollector as datacollector
import subprocess
import ssl
import socket
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logger as logging

def get_ssl_details_check(host, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        issued_date = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_remaining = (expiry_date - datetime.datetime.utcnow()).days
        issuer = dict(x[0] for x in cert['issuer'])['commonName']
        commonName = dict(x[0] for x in cert['subject'])['commonName']
        serialNumber = cert['serialNumber']
        return issued_date, expiry_date, issuer, days_remaining, commonName, serialNumber
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [ 400, 404]:
            sys.exit(1)
        return None, None, None, None, None, None

def add_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact):
    try:
        # Read all lines
        issued_date, expiry, issuer, days_remaining, commonName, serialNumber = get_ssl_details_check(target_host, target_port)
        if expiry:
            Cert_details = {
                "System Name" : target_system,
                "Host" : target_host,
                "Port" : target_port,
                "Certificate Issuer" : issuer, 
                "Issue Date": issued_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Expiry Date": expiry.strftime("%Y-%m-%d %H:%M:%S"),
                "No of Dats Remainng" : days_remaining,
                "Common Name" : commonName,
                "Serial Number" : serialNumber
            }
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Request for adding an entry has been submitted')
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Below are the certificates')
            logging.logger('INFO', 'Certificate Viewer Tool', 200, Cert_details)
            with open(file_path, 'r') as file:
                lines = file.readlines()

            header = lines[0]  # Preserve header
            updated_lines = [header]

            found = False

            # Iterate over remaining lines
            for line in lines[1:]:
                system, host, port, team_email, manager_email, emergency_contact = line.strip().split("|")

                # If host and port match — replace line
                if host == target_host and port == target_port and target_system == system:
                    updated_lines.append(line + '\n')
                    logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Certificate match has been found')
                    found = True
                else:
                    updated_lines.append(line if line.endswith('\n') else line + '\n')

            if found:
                logging.logger('INFO', 'Certificate Viewer Tool', 200, f"Entry Already exists please go to update section to update the data")
                return "Entry Already exists please go to update section to update the data"
            else:
                #new entry
                new_entry = f'{target_system}|{target_host}|{target_port}|{target_team_email}|{target_manager_email}|{target_contact}'
                updated_lines.append(new_entry + '\n')
                with open(file_path, 'w') as file:
                    file.writelines(updated_lines)
                logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Added the certificate entry to the backend entry file')
                logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Refreshing the certificate data')
                datacollector.certificateDataCollector()
                logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Refreshing of the certificate data has been completed')
                return "Entery Added Successfully"
        else:
            logging.logger('INFO', 'Certificate Viewer Tool', 200, "Error Getting the Certificate details and hence unable to add")
            return "Error Getting the Certificate details and hence unable to add"
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [ 400, 404]:
            sys.exit(1)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, "Error Getting the Certificate details and hence unable to add")
        return "Error Getting the Certificate details and hence unable to add"


# Example usage
# file_path = 'C:\\Users\\shankara.nanjangudga\\Desktop\\pythonscript\\certificatewebsite\\backend_systems.lst'
# target_host = 'shankar.com'
# target_port = '443'
# target_system = 'shankar'
# target_team_email = 'newteam@gmail.com'
# target_manager_email = 'newmanager@gmail.com'
# target_contact = '1234567890'

# add_backend_entry(file_path, target_host, target_port, target_system, target_team_email, target_manager_email, target_contact)
