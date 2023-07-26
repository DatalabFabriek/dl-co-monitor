#!/usr/bin/python
# -------------------------------------------------------------------
# @copyright 2017 DennyZhang.com
# Licensed under MIT
#   https://www.dennyzhang.com/wp-content/mit_license.txt
#
# @copyright 2023 Harmen van der Veer for the portions adopted 
# for service rather than container monitoring
# File : monitor-docker-slack.py
# Author : Denny <https://www.dennyzhang.com/contact>
# Author : Harmen van der Veer <harmen@datalab.nl>
# Description :
# --
# Created : <2017-08-20>
# Updated: Time-stamp: <2023-07-27 16:36:53>
# -------------------------------------------------------------------
import argparse
import json
import re
import time

import requests_unixsocket
import requests

from datetime import datetime


def name_in_list(name, name_pattern_list):
    for name_pattern in name_pattern_list:
        if re.search(name_pattern, name) is not None:
            return True
    return False


################################################################################

def list_services_by_sock(docker_sock_file):
    session = requests_unixsocket.Session()
    container_list = []
    socket = docker_sock_file.replace("/", "%2F")
    url = "http+unix://%s/%s" % (socket, "services?all=1&status=TRUE")
    r = session.get(url)
    # TODO: error handling
    assert r.status_code == 200
    for service in json.loads(r.content):
        item = (service["Spec"]["Name"], service["ServiceStatus"]["RunningTasks"], service["ServiceStatus"]["DesiredTasks"])
        container_list.append(item)
    return container_list

def get_unhealthy_services(service_list):
    return [service for service in service_list if service[1] < service[2]]

# TODO: simplify this by lambda
def services_remove_by_name_pattern(service_list, name_pattern_list):
    if len(name_pattern_list) == 0:
        return service_list

    l = []
    for service in service_list:
        names, running, desired = service
        for name in names:
            if name_in_list(name, name_pattern_list):
                break
        else:
            l.append(service)
    return l

def service_list_to_str(service_list):
    msg = ""
    for service in service_list:
        names, running, desired = service
        msg = f"{names}: {running}/{desired}\n{msg}"
    return msg

def monitor_docker_slack(docker_sock_file, white_pattern_list):
    services_list = list_services_by_sock(docker_sock_file)
    unhealthy_services_list = get_unhealthy_services(services_list)

    unhealthy_services_list = services_remove_by_name_pattern(unhealthy_services_list, white_pattern_list)

    err_msg = ""

    number_of_unhealthy_services_list = len(unhealthy_services_list)
    
    if number_of_unhealthy_services_list != 0:
        err_msg = "Detected Unhealthy Services: \n%s\n%s" % (service_list_to_str(unhealthy_services_list), err_msg)

    if err_msg == "":
        return "OK", "Everything seems to be back to normal, all services have the same number of running replicas as target replicas"
    else:
        return "ERROR", err_msg

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slack_webhook', required=True, help="Slack webhook to post alerts.", type=str)
    parser.add_argument('--whitelist', default='', required=False,
                        help="Skip checking certain services. A list of regexp separated by comma.", type=str)
    parser.add_argument('--check_interval', default='300', required=False, help="Periodical check. By seconds.",
                        type=int)
    parser.add_argument('--msg_prefix', default='', required=False, help="Slack message prefix.", type=str)
    l = parser.parse_args()
    check_interval = l.check_interval
    white_pattern_list = l.whitelist.split(',')

    if white_pattern_list == ['']:
        white_pattern_list = []

    slack_webhook = l.slack_webhook
    msg_prefix = l.msg_prefix

    if slack_webhook == '':
        print("Warning: Please provide slack webhook, to receive alerts properly.")

    requests.post(slack_webhook, data=json.dumps({'text': f"{msg_prefix}:\nMonitoring of Docker Services started"}))

    has_send_error_alert = False
    previous_err_msg = ''

    while True:
        now = datetime.now()
        (status, err_msg) = monitor_docker_slack("/var/run/docker.sock", white_pattern_list)

        if msg_prefix != "":
            err_msg = "%s:\n%s" % (msg_prefix, err_msg)
        
        if status == "OK":
            if has_send_error_alert is True:
                print(f"[{now}]  {err_msg}")
                requests.post(slack_webhook, data=json.dumps({'text': f"[{now}]  {err_msg}"}))
                has_send_error_alert = False
        else:
            if has_send_error_alert is False or previous_err_msg != err_msg:
                print(f"[{now}]  {err_msg}")
                requests.post(slack_webhook, data=json.dumps({'text': f"[{now}]  {err_msg}"}))
                # avoid send alerts over and over again
                # but DO SEND if error message has changed (could mean other services have crashed)
                has_send_error_alert = True
                
        previous_err_msg = err_msg
        time.sleep(check_interval)
# File : monitor-docker-slack.py ends