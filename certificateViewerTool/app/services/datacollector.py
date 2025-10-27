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
import configloader as cnfloader
import logger as logging

def get_ssl_details(host, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        # issued_date = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        # expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        # days_remaining = (expiry_date - datetime.datetime.utcnow()).days
        issued_date = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z').replace(tzinfo=datetime.UTC)
        expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z').replace(tzinfo=datetime.UTC)
        days_remaining = (expiry_date - datetime.datetime.now(datetime.UTC)).days
        issuer = dict(x[0] for x in cert['issuer'])['commonName']
        commonName = dict(x[0] for x in cert['subject'])['commonName']
        serialNumber = cert['serialNumber']
        return issued_date, expiry_date, issuer, days_remaining, commonName, serialNumber
    except Exception as e:
        config = cnfloader.load_properties()
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [ 400, 404]:
            sys.exit(1)
        return None, None, None, None, None, None

def sort_certificate_report(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    header = lines[0]
    data_lines = lines[1:]

    # Sort by days (7th index, zero-based)
    sorted_data = sorted(data_lines, key=lambda x: int(x.strip().split("|")[8]))

    with open(file_path, 'w') as f:
        f.write(header)
        for line in sorted_data:
            f.write(line)

def certificateDataCollector():
    try:
        config = cnfloader.load_properties()
        results = []
        results.append(f'System|Host|Port|Common Name|Serial Number|Issuer|Issued Date|expiry|Days Remaining|Team email|Manager Email|Emergency Contact')
        pathForTheDirectory = config.get('dataDirectory')
        applicationlistfile = config.get('systemFiles')
        if not pathForTheDirectory or not applicationlistfile:
            raise ValueError((400, "Missing 'dataDirectory' or 'systemFiles' in config"))
        fullpath = os.path.join(pathForTheDirectory, applicationlistfile)
        if not os.path.exists(fullpath):
            raise FileNotFoundError(f"File not found: {fullpath}")

        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Collecting Live data of the certificates')
        with open(fullpath) as f:
            next(f)
            for line in f:
                system, host, port, team_email, manager_email, emergency_contact  = line.strip().split("|")
                issued_date, expiry, issuer, days_remaining, commonName, serialNumber = get_ssl_details(host, port)
                if expiry:
                    temp_result = f'{system}|{host}|{port}|{commonName}|{serialNumber}|{issuer}|{issued_date}|{expiry}|{days_remaining}|{team_email}|{manager_email}|{emergency_contact}'
                    results.append(temp_result)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Certificate Data has been collected')
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Writing the certificate data to file')
        certificateReportFile = config.get('certificateReport')
        if not pathForTheDirectory or not certificateReportFile:
            raise ValueError((400, "Missing 'dataDirectory' or 'certificateReport' in config"))
        certificatefullpath = os.path.join(pathForTheDirectory, certificateReportFile)
        if not os.path.exists(certificatefullpath):
            with open(certificatefullpath, 'w') as f:
                pass
        with open(certificatefullpath, 'w') as output_file:
            for item in results:
                output_file.write(item + '\n')
        logging.logger('INFO', 'Certificate Viewer Tool', 200, f'Certificate Data has been written in the following file {certificatefullpath}')
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Proceeding to sort it based on the expiry')
        red = []
        yellow = []
        green = []
        red.append(f'System|Host|Port|Common Name|Serial Number|Issuer|Issued Date|expiry|Days Remaining|Team email|Manager Email|Emergency Contact')
        yellow.append(f'System|Host|Port|Common Name|Serial Number|Issuer|Issued Date|expiry|Days Remaining|Team email|Manager Email|Emergency Contact')
        green.append(f'System|Host|Port|Common Name|Serial Number|Issuer|Issued Date|expiry|Days Remaining|Team email|Manager Email|Emergency Contact')
        
        with open(certificatefullpath) as f:
            next(f)
            for line in f:
                system, host, port, commonName, serialNumber, issuer, issued_date, expiry, days_remaining, team_email, manager_email, emergency_contact  = line.strip().split("|")
                days_remaining = int(days_remaining)
                if (days_remaining<=15):
                    temp_result = f'{system}|{host}|{port}|{commonName}|{serialNumber}|{issuer}|{issued_date}|{expiry}|{days_remaining}|{team_email}|{manager_email}|{emergency_contact}'
                    red.append(temp_result)
                elif (days_remaining<=30 and days_remaining>15):
                    temp_result = f'{system}|{host}|{port}|{commonName}|{serialNumber}|{issuer}|{issued_date}|{expiry}|{days_remaining}|{team_email}|{manager_email}|{emergency_contact}'
                    yellow.append(temp_result)
                else:
                    temp_result = f'{system}|{host}|{port}|{commonName}|{serialNumber}|{issuer}|{issued_date}|{expiry}|{days_remaining}|{team_email}|{manager_email}|{emergency_contact}'
                    green.append(temp_result)
        
        greenCertificateReportFile = config.get('greenReport')
        yellowCertificateReportFile = config.get('yellowReport')
        redCertificateReportFile = config.get('redReport')
        if not greenCertificateReportFile or not yellowCertificateReportFile or not redCertificateReportFile:
            raise ValueError((400, "Missing 'dataDirectory' or 'certificateReport' in config"))
        greenCertificateReportFilePath = os.path.join(pathForTheDirectory, greenCertificateReportFile)
        yellowCertificateReportFilePath = os.path.join(pathForTheDirectory, yellowCertificateReportFile)
        redCertificateReportFilePath = os.path.join(pathForTheDirectory, redCertificateReportFile)
        if not os.path.exists(greenCertificateReportFilePath):
            with open(greenCertificateReportFilePath, 'w') as f:
                pass
        if not os.path.exists(yellowCertificateReportFilePath):
            with open(yellowCertificateReportFilePath, 'w') as f:
                pass
        if not os.path.exists(redCertificateReportFilePath):
            with open(redCertificateReportFilePath, 'w') as f:
                pass        
        with open(greenCertificateReportFilePath, 'w') as output_file:
            for item in green:
                output_file.write(item + '\n')

        with open(yellowCertificateReportFilePath, 'w') as output_file:
            for item in yellow:
                output_file.write(item + '\n')

        with open(redCertificateReportFilePath, 'w') as output_file:
            for item in red:
                output_file.write(item + '\n')
                
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Sorting has been completed')
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Arranging the certificates according to the expiry dates')
        sort_certificate_report(redCertificateReportFilePath)
        sort_certificate_report(yellowCertificateReportFilePath)
        sort_certificate_report(greenCertificateReportFilePath)
        sort_certificate_report(certificatefullpath)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Arrangement of the certificates have been compeleted')       
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [ 400, 404]:
            sys.exit(1)

      

    # report_html = generate_html_report(results)
    # send_email(report_html, "BELL WEST SSL Report", "bell.qualification.services.mas@cgi.com", "shankara.nanjangudgangadhara@cgi.com")

# certificateDataCollector()
