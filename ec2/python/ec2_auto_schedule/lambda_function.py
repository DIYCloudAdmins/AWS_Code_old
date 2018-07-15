#python 2.7
#created by Paul Beauvais
#requires pytz, json, datetime packages
#shuts down ec2 instances based on schedule in autoSchedule tag in ec2 instance.
# tag format: "shutdown:yes;shutdownHour:01;shutdownDays:mon,tue,wed,thur,fri,sat,sun;startup:yes;startupHour:1;startupDays:mon,tue,wed,thur,fri,sat"
# hours are in 24 hour code and on eastern time.  All hours must have 2 digits (03 and 15 are 3am and 3pm respecitvly)


import AS_Helper
import boto3
import json

def evaluateTag(tagValue):
    
    configlist = tagValue.split(";")

    returnMessage = "noAction"
    
    schedule = AS_Helper.evaluateSchedule(configlist)
    if ( 
        schedule.shutdown == True and schedule.shutdownHourMatch == True and schedule.shutdownToday == True
        ):
            returnMessage = "shutDown"
    if (
        schedule.startup == True and schedule.startupHourMatch == True and schedule.startupToday == True
        ):
            returnMessage = "startUp"
    return returnMessage

def identifyInstances():

    outMsg=[] 
    print("starting EC2 AutoScheduler")
    tagkey="autoSchedule"
    client=boto3.client('ec2')
    ec2inst=boto3.resource('ec2')
    response=client.describe_instances(
        Filters = [{'Name': 'tag:autoSchedule', 'Values': ['*']},{'Name': 'instance-state-name','Values': ['running']}]
    )
      
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instanceID = instance["InstanceId"]
            EC2instance = ec2inst.Instance(instanceID)
            for tags in EC2instance.tags:
                if tags["Key"] == 'Name':
                    instanceName = (tags["Value"])
                if tags["Key"] == "autoSchedule":
                    tagSchedule = (tags["Value"])
                    tagAction = evaluateTag(tagSchedule)
            if tagAction == "shutDown":
                print(instanceID  + " - " + instanceName + " - stoping")
            if tagAction == "startUp":
                print(instanceID  + " - " + instanceName + " - starting")


    return "completed autoSchedule Sequence"

def lambda_handler(event, context):
    x = identifyInstances()
    print(x)
