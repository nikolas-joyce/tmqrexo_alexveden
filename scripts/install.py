import os, sys

try:
    from .settings import *
except SystemError:
    from scripts.settings import *


supervisor_config_dir = 'supervisor_include'
current_path = sys.path[0]

TMQRPATH = os.getenv('TMQRPATH', '/var/data/tmqrengine')
PYTHONPATH = os.getenv('PYTHONPATH', '/var/data/tmqrengine')

def stop():
    os.system('service supervisor stop')

def clean():
    print("Removing: ./supervisor_include/*.conf")
    os.system('rm ./supervisor_include/*.conf')

    print("Removing: /etc/cron.weekly/tmqr_*.py")
    os.system('rm /etc/cron.weekly/tmqr_*.py')


def start():
    os.system('service supervisor start')


def pre_setup():
    # Create supervisor config dir
    if not os.path.exists(os.path.join(current_path, supervisor_config_dir)):
        os.mkdir(os.path.join(current_path, supervisor_config_dir))

    if not os.path.exists(os.path.join(current_path, 'logs')):
        os.mkdir(os.path.join(current_path, 'logs'))

def install_exo_online():
    if not os.path.exists(os.path.join(current_path, 'logs', 'exo')):
        os.mkdir(os.path.join(current_path, 'logs', 'exo'))

    for instr in INSTRUMENTS_LIST:
        if not os.path.exists(os.path.join(current_path, 'logs', 'exo', instr)):
            os.mkdir(os.path.join(current_path, 'logs', 'exo', instr))

        supervisor_conf_template = """[program:EXO_{instrument}]
command=python3.5 {script_file} -v --debug={debug_logdir} {instrument}
stderr_logfile={stderr_log}
stderr_logfile_maxbytes=1MB

stdout_logfile={stdout_log}
stdout_logfile_maxbytes=1MB
startsecs=30
autostart=true
startretries=5
directory={current_path}
environment=TMQRPATH="{tmqrpath}",PYTHONPATH="{pythonpath}"
"""


        file_contents = supervisor_conf_template.format(**{
            'instrument': instr,
            'script_file': 'exo_builder.py',
            'stdout_log': os.path.join(current_path, 'logs', 'exo', 'exo_builder_{0}_stdout.log'.format(instr)),
            'stderr_log': os.path.join(current_path, 'logs', 'exo', 'exo_builder_{0}_stderr.log'.format(instr)),
            'current_path': current_path,
            'debug_logdir': os.path.join(current_path, 'logs', 'exo', instr),
            'tmqrpath': TMQRPATH,
            'pythonpath': PYTHONPATH,
        })

        file_name = 'exo_{0}.conf'.format(instr).lower()
        print('install_exo_online(): Writing '+file_name)
        with open(os.path.join(current_path, supervisor_config_dir, file_name), 'w') as fh:
            fh.write(file_contents)

def install_quotes_notifications():
    if not os.path.exists(os.path.join(current_path, 'logs', 'quotes')):
        os.mkdir(os.path.join(current_path, 'logs', 'quotes'))

    for instr in INSTRUMENTS_LIST:
        supervisor_conf_template = """[program:QUOTES_{instrument}]
command=python3.5 {script_file} -v {instrument}
stderr_logfile={stderr_log}
stderr_logfile_maxbytes=1MB

stdout_logfile={stdout_log}
stdout_logfile_maxbytes=1MB
directory={current_path}
startsecs=30
autostart=true
startretries=5
environment=TMQRPATH="{tmqrpath}",PYTHONPATH="{pythonpath}"
"""


        file_contents = supervisor_conf_template.format(**{
            'instrument': instr,
            'script_file': 'quotes_notification.py',
            'stdout_log': os.path.join(current_path, 'logs', 'quotes', 'quotes_notification_{0}_stdout.log'.format(instr)),
            'stderr_log': os.path.join(current_path, 'logs', 'quotes', 'quotes_notification_{0}_stderr.log'.format(instr)),
            'current_path': current_path,
            'tmqrpath': TMQRPATH,
            'pythonpath': PYTHONPATH,
        })

        file_name = 'quotes_{0}.conf'.format(instr).lower()
        print('install_quotes_notifications(): Writing '+file_name)
        with open(os.path.join(current_path, supervisor_config_dir, file_name), 'w') as fh:
            fh.write(file_contents)

def install_alphas_online():
    if not os.path.exists(os.path.join(current_path, 'logs', 'alphas')):
        os.mkdir(os.path.join(current_path, 'logs', 'alphas'))

    for alpha_name in ALPHAS_GENERIC:
        supervisor_conf_template = """[program:ALPHA_GENERIC_{instrument}]
command=python3.5 {script_file} -v {instrument}
stderr_logfile={stderr_log}
stderr_logfile_maxbytes=1MB

stdout_logfile={stdout_log}
stdout_logfile_maxbytes=1MB
directory={current_path}
startsecs=30
autostart=true
startretries=5
environment=TMQRPATH="{tmqrpath}",PYTHONPATH="{pythonpath}"
"""


        file_contents = supervisor_conf_template.format(**{
            'instrument': alpha_name,
            'script_file': 'alpha_online.py',
            'stdout_log': os.path.join(current_path, 'logs', 'alphas', 'generic_{0}_stdout.log'.format(alpha_name)),
            'stderr_log': os.path.join(current_path, 'logs', 'alphas', 'generic_{0}_stderr.log'.format(alpha_name)),
            'current_path': current_path,
            'tmqrpath': TMQRPATH,
            'pythonpath': PYTHONPATH,
        })

        file_name = 'alpha_generic_{0}.conf'.format(alpha_name).lower()
        print('install_alphas_online(): Writing '+file_name)
        with open(os.path.join(current_path, supervisor_config_dir, file_name), 'w') as fh:
            fh.write(file_contents)


def install_alphas_custom():
    if not os.path.exists(os.path.join(current_path, 'logs', 'alphas', 'custom')):
        os.mkdir(os.path.join(current_path, 'logs', 'alphas', 'custom'))

    for alpha_custom_exo_name in ALPHAS_CUSTOM:
        supervisor_conf_template = """[program:ALPHA_CUSTOM_{instrument}]
command=python3.5 {script_file} -v {instrument}
stderr_logfile={stderr_log}
stderr_logfile_maxbytes=1MB

stdout_logfile={stdout_log}
stdout_logfile_maxbytes=1MB
directory={current_path}
startsecs=30
autostart=true
startretries=5
environment=TMQRPATH="{tmqrpath}",PYTHONPATH="{pythonpath}"
"""


        file_contents = supervisor_conf_template.format(**{
            'instrument': alpha_custom_exo_name,
            'script_file': 'alpha_online_custom.py',
            'stdout_log': os.path.join(current_path, 'logs', 'alphas', 'custom', 'custom_{0}_stdout.log'.format(alpha_custom_exo_name)),
            'stderr_log': os.path.join(current_path, 'logs', 'alphas', 'custom', 'custom_{0}_stderr.log'.format(alpha_custom_exo_name)),
            'current_path': current_path,
            'tmqrpath': TMQRPATH,
            'pythonpath': PYTHONPATH,
        })

        file_name = 'alpha_custom_{0}.conf'.format(alpha_custom_exo_name).lower()
        print('install_alphas_custom(): Writing '+file_name)
        with open(os.path.join(current_path, supervisor_config_dir, file_name), 'w') as fh:
            fh.write(file_contents)

def install_trading_script():
    if not os.path.exists(os.path.join(current_path, 'logs', 'trading')):
        os.mkdir(os.path.join(current_path, 'logs', 'trading'))

    supervisor_conf_template = """[program:TRADING_ONLINE]
command=python3.5 {script_file} -v
stderr_logfile={stderr_log}
stderr_logfile_maxbytes=1MB

stdout_logfile={stdout_log}
stdout_logfile_maxbytes=1MB
directory={current_path}
startsecs=30
autostart=true
startretries=5
environment=TMQRPATH="{tmqrpath}",PYTHONPATH="{pythonpath}"
"""


    file_contents = supervisor_conf_template.format(**{
        'script_file': 'trading_online.py',
        'stdout_log': os.path.join(current_path, 'logs', 'trading', 'trading_online_stdout.log'),
        'stderr_log': os.path.join(current_path, 'logs', 'trading', 'trading_online_stderr.log'),
        'current_path': current_path,
        'tmqrpath': TMQRPATH,
        'pythonpath': PYTHONPATH,
    })

    file_name = 'trading_online.conf'
    print('install_alphas_custom(): Writing '+file_name)
    with open(os.path.join(current_path, supervisor_config_dir, file_name), 'w') as fh:
        fh.write(file_contents)

def install_cron_alpha_rebalancer():
    if not os.path.exists(os.path.join(current_path, 'logs', 'scheduled')):
        os.mkdir(os.path.join(current_path, 'logs', 'scheduled'))

    script_source = """#!/bin/sh
export PYTHONPATH={pythonpath}
export TMQRPATH={tmqrpath}
cd {current_path}
python3.5 {current_path}/{script_file} -v --logfile={log_file}
"""

    file_contents = script_source.format(**{
        'script_file': 'alpha_rebalancer.py',
        'log_file': os.path.join(current_path, 'logs', 'scheduled', 'alpha_rebalancer.log'),
        'current_path': current_path,
        'tmqrpath': TMQRPATH,
        'pythonpath': PYTHONPATH,
    })

    file_name = '/etc/cron.weekly/tmqr_alpha_rebalancer.sh'
    print('install_cron_alpha_rebalancer(): Writing ' + file_name)
    with open(file_name, 'w') as fh:
        fh.write(file_contents)

    os.system('chmod +x {0}'.format(file_name))

def install_cron_assetindex_updater():
    if not os.path.exists(os.path.join(current_path, 'logs', 'scheduled')):
        os.mkdir(os.path.join(current_path, 'logs', 'scheduled'))

    script_source = """#!/bin/sh
export PYTHONPATH={pythonpath}
export TMQRPATH={tmqrpath}
cd {current_path}
python3.5 {current_path}/{script_file} -v --logfile={log_file}
"""

    file_contents = script_source.format(**{
        'script_file': 'assetindex_updater.py',
        'log_file': os.path.join(current_path, 'logs', 'scheduled', 'assetindex_updater.log'),
        'current_path': current_path,
        'tmqrpath': TMQRPATH,
        'pythonpath': PYTHONPATH,
    })

    file_name = '/etc/cron.weekly/tmqr_assetindex_updater.sh'
    print('install_cron_assetindex_updater(): Writing ' + file_name)
    with open(file_name, 'w') as fh:
        fh.write(file_contents)

    os.system('chmod +x {0}'.format(file_name))




if __name__ == '__main__':
    print('TMQR Execution layer installation script')
    print('This script will overwrite all previous settings. Proceed? (y/n)')

    input_value = input()

    if input_value.lower() != 'y' or input_value.lower() != 'yes':
        print('Terminating...')

    # Stopping services
    stop()

    # Clean all configs
    clean()

    # Run pre-setup
    pre_setup()

    # Setting up scripts
    install_exo_online()
    install_quotes_notifications()
    install_alphas_online()
    install_alphas_custom()
    install_trading_script()

    # Setting up CRON scripts
    install_cron_alpha_rebalancer()
    install_cron_assetindex_updater()

    # Starting services
    start()

