from flask import Flask, render_template, request, redirect, url_for, session
import os
import services.fileupdater as fileupdater
import services.fileadd as fileadd
import services.fileremove as fileremove
import services.datacollector as datacollector
import services.applicationstart as applicationstart
from flask import jsonify
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import configloader as cnfloader
import logger as logging

app = Flask(__name__)
app.secret_key = 'yoursecretkey'

# Helper function to count lines
def count_lines(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return len(f.readlines()) - 1  # subtract header
    return 0

# Helper to read data from file
def read_report(filepath):
    if not os.path.exists(filepath):
        return [], []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        headers = lines[0].strip().split("|")
        data = [line.strip().split("|") for line in lines[1:]]
    return headers, data

@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading the Logging in page')
        if request.method == 'POST':
            if request.form['username'] == 'admin' and request.form['password'] == 'password':
                session['logged_in'] = True
                logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Redirectng to Dashboard Page')
                return redirect(url_for('dashboard'))
    
        renderingloginpage = render_template('login.html', title="Login")
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Login Page Loaded Successfully')
        return renderingloginpage
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

@app.route('/dashboard')
def dashboard():
    try:
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in Redirecting to logging in page')
            return redirect(url_for('login'))
        
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Dashboard Page')
        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        greenFile = config.get('greenReport')
        yellowFile = config.get('yellowReport')
        redFile = config.get('redReport')
        if not datafilepath or not greenFile or not yellowFile or not redFile:
            raise ValueError((400, "Missing paths in config"))
        greenFilePath = os.path.join(datafilepath,greenFile)
        yellowFilePath = os.path.join(datafilepath,yellowFile)
        redFilePath = os.path.join(datafilepath,redFile)
        if not os.path.exists(greenFilePath):
            raise FileNotFoundError((400,f"File not found: {greenFilePath}"))
        if not os.path.exists(yellowFilePath):
            raise FileNotFoundError((400,f"File not found: {yellowFilePath}"))
        if not os.path.exists(redFilePath):
            raise FileNotFoundError((400,f"File not found: {redFilePath}"))

        green_count = count_lines(greenFilePath)
        yellow_count = count_lines(yellowFilePath)
        red_count = count_lines(redFilePath)
        
        dashboardpage = render_template('dashboard.html', 
            title="Dashboard",
            green_count=green_count, 
            yellow_count=yellow_count, 
            red_count=red_count,
            logged_in=True
        )

        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Dashboard Page Loaded Successfully')
        return dashboardpage
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None


@app.route('/view/<color>')
def view_report(color):
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Certificates and all the reports')
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in redirecting to login page')
            return redirect(url_for('login'))

        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        greenFile = config.get('greenReport')
        yellowFile = config.get('yellowReport')
        redFile = config.get('redReport')
        if not datafilepath or not greenFile or not yellowFile or not redFile:
            raise ValueError((400, "Missing paths in config"))
        greenFilePath = os.path.join(datafilepath,greenFile)
        yellowFilePath = os.path.join(datafilepath,yellowFile)
        redFilePath = os.path.join(datafilepath,redFile)
        if not os.path.exists(greenFilePath):
            raise FileNotFoundError((400,f"File not found: {greenFilePath}"))
        if not os.path.exists(yellowFilePath):
            raise FileNotFoundError((400,f"File not found: {yellowFilePath}"))
        if not os.path.exists(redFilePath):
            raise FileNotFoundError((400,f"File not found: {redFilePath}"))

        file_paths = {
            'green': greenFilePath,
            'yellow': yellowFilePath,
            'red': redFilePath
        }

        if color not in file_paths:
            return "Invalid report color", 404

        headers, data = read_report(file_paths[color])

        certificateview = render_template('view_report.html', 
            title=f"{color.capitalize()} Certificate Report", 
            headers=headers, 
            data=data,
            logged_in=True
        )

        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Certificates Loaded Successfully')
        return certificateview
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Search Page')
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in redirecting to login page')
            return redirect(url_for('login'))

        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        certificateReportFile = config.get('certificateReport')
        if not datafilepath or not certificateReportFile:
            raise ValueError((400, "Missing paths in config"))
        certificateReportFilePath = os.path.join(datafilepath,certificateReportFile)
        if not os.path.exists(certificateReportFilePath):
            raise FileNotFoundError((400,f"File not found: {certificateReportFilePath}"))


        filepath = certificateReportFilePath
        headers, data = read_report(filepath)

        search_results = data
        query = ""

        if request.method == 'POST':
            query = request.form.get('query', '').lower()
            search_results = [row for row in data if query in '|'.join(row).lower()]

        searchpageloader = render_template('search.html',
                        title="Search Certificates",
                        headers=headers,
                        data=search_results,
                        query=query,
                        logged_in=True)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Search page loaded successfully')
        return searchpageloader
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None


@app.route('/update', methods=['GET', 'POST'])
def update():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Update Page')
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in redirecting to login page')
            return redirect(url_for('login'))
        
        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        systemFiles = config.get('systemFiles')
        if not datafilepath or not systemFiles:
            raise ValueError((400, "Missing paths in config"))
        systemFilesPath = os.path.join(datafilepath,systemFiles)
        if not os.path.exists(systemFilesPath):
            raise FileNotFoundError((400,f"File not found: {systemFilesPath}"))

        if request.method == 'POST':
            file_path = systemFilesPath
            target_system = request.form.get('target_system')
            target_host = request.form.get('target_host')
            target_port = request.form.get('target_port')
            target_team_email = request.form.get('target_team_email')
            target_manager_email = request.form.get('target_manager_email')
            target_contact = request.form.get('target_contact')

            success = fileupdater.update_backend_entry(
                file_path, target_host, target_port, target_system,
                target_team_email, target_manager_email, target_contact
            )

            if success:
                return jsonify({'message': "File updated successfully."})
            else:
                return jsonify({'message': "No matching entry found for the provided Host, Port, and System."})

        # If GET request, show the form
        updatepage = render_template('update.html', title="Update Backend Entry", logged_in=True)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Update Page Loaded Successfully')
        return updatepage
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

@app.route('/add', methods=['GET', 'POST'])
def add():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Add Page')
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in redirecting to login page')
            return redirect(url_for('login'))
        
        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        systemFiles = config.get('systemFiles')
        if not datafilepath or not systemFiles:
            raise ValueError((400, "Missing paths in config"))
        systemFilesPath = os.path.join(datafilepath,systemFiles)
        if not os.path.exists(systemFilesPath):
            raise FileNotFoundError((400,f"File not found: {systemFilesPath}"))

        if request.method == 'POST':
            file_path = systemFilesPath
            target_system = request.form.get('target_system')
            target_host = request.form.get('target_host')
            target_port = request.form.get('target_port')
            target_team_email = request.form.get('target_team_email')
            target_manager_email = request.form.get('target_manager_email')
            target_contact = request.form.get('target_contact')

            result_message = fileadd.add_backend_entry(
                file_path, target_host, target_port, target_system,
                target_team_email, target_manager_email, target_contact
            )

            return jsonify({'message': result_message})

        addpage = render_template('add.html', title="Add Backend Entry", logged_in=True)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Adding Page Loaded Successfully')
        return addpage
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None
    
@app.route('/remove', methods=['GET', 'POST'])
def remove():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loading Remove Page')
        if not session.get('logged_in'):
            logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Not Logged in redirecting to login page')
            return redirect(url_for('login'))

        config = cnfloader.load_properties()
        datafilepath = config.get('dataDirectory')
        systemFiles = config.get('systemFiles')
        if not datafilepath or not systemFiles:
            raise ValueError((400, "Missing paths in config"))
        systemFilesPath = os.path.join(datafilepath,systemFiles)
        if not os.path.exists(systemFilesPath):
            raise FileNotFoundError((400,f"File not found: {systemFilesPath}"))

        if request.method == 'POST':
            file_path = systemFilesPath
            target_system = request.form.get('target_system')
            target_host = request.form.get('target_host')
            target_port = request.form.get('target_port')
            target_team_email = request.form.get('target_team_email')
            target_manager_email = request.form.get('target_manager_email')
            target_contact = request.form.get('target_contact')

            result_message = fileremove.remove_backend_entry(
                file_path, target_host, target_port, target_system,
                target_team_email, target_manager_email, target_contact
            )

            return jsonify({'message': result_message})

        removepage = render_template('remove.html', title="Delete Backend Entry", logged_in=True)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Remove Page Loaded Successfully')
        return removepage
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

@app.route('/logout')
def logout():
    try:
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loggin Out')
        session.pop('logged_in', None)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Loggin Out Successfully')
        return redirect(url_for('login'))
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
        return None

if __name__ == '__main__':
    try:
        statUpMessage = applicationstart.intro()
        datacollector.certificateDataCollector()
        logging.startinglogger(statUpMessage)
        logging.logger('INFO', 'Certificate Viewer Tool', 200, 'Starting the Application')
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        if isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, message = e.args[0]
        else:
            code, message = 500, str(e)
        logging.logger('ERROR', 'Certificate Viewer Tool', code, message)
        if code in [400, 404]:
            sys.exit(1)
