#-*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys
import os
import csv
from multiprocessing import Process, Queue
import time
from datetime import datetime
import getopt
import configparser

class Args(object):
    def __init__(self):
        try:
            self.opts = getopt.getopt(sys.argv[1:],"C:c:d:o:")
            self.options = self.opts[0]
            #print(self.options)
        except getopt.GetoptError:
            print('getopt Error')

    def get_arg(self,index_arg):
        output = ''
        #print(self.options)
        try:
            for opt,arg in self.options:
                #print(opt,arg)
                if opt == index_arg:
                    output = arg
                else:
                    continue
        except ValueError:
            print('Argument Error')
        #print(output)
        return output

class Config(object):
    def __init__(self, args):
        self.config = self._read_config(args)

    def _read_config(self,args):
        config = {}
        configparse = configparser.ConfigParser()
        configfile = args.get_arg('-c')
        #print(configfile)
        configparse.read(configfile)
        configsection = args.get_arg('-C').upper()
        #print(configsection)
        for option in configparse.options(configsection):
            #print(option)
            config[option] = float(configparse[configsection][option])
            #print(config)
        return config

    def get_config(self,arg):
        return self.config[arg]

class UserData(object):
    def __init__(self,args,task_queue):
        self.task_queue = task_queue
        self.userdata = self._read_users_data(args)

    def _read_users_data(self,args):
        userdata = []
        userfile = args.get_arg('-d')
        with open(userfile) as file:
            for line in file:
                try:
                    i = line.split(',')
                    user_message = (i[0],int(i[1]))
                    userdata.append(user_message)
                except ValueError:
                    print('UserData Error')
        return userdata

    def send_userdata(self):
        for user in self.userdata:
            self.task_queue.put(user)
            #print(user)
            #self.task_queue.task_done()
        return

class IncomeTaxCalculator(object):
    def __init__(self,config,args,task_queue,result_queue):
        self.config = config
        self.args = args
        self.task_queue = task_queue
        self.result_queue = result_queue

    def calc_for_all_userdata(self):
        time.sleep(0.1)
        jsl = self.config.get_config('JiShuL'.lower())
        jsh = self.config.get_config('JiShuH'.lower())
        yla = self.config.get_config('YangLao'.lower())
        yli = self.config.get_config('YiLiao'.lower())
        sye = self.config.get_config('ShiYe'.lower())
        gs = self.config.get_config('GongShang'.lower())
        syu = self.config.get_config('ShengYu'.lower())
        gjj = self.config.get_config('GongJiJin'.lower())
        #print(gjj)
        if not self.task_queue.empty():
            for i in range(self.task_queue.qsize()):
                user_m = self.task_queue.get()
                #print(user_m)
                worker_id = user_m[0]
                salary = user_m[1]
                if salary < jsl:
                    insure5_1 = jsl*(yla+yli+sye+gs+syu+gjj)
                elif salary > jsh:
                    insure5_1 = jsh*(yla+yli+sye+gs+syu+gjj)
                else:
                    insure5_1 = salary*(yla+yli+sye+gs+syu+gjj)
            
                taxable_salary = salary - insure5_1 -3500
                if taxable_salary < 0:
                    tax = 0
                elif taxable_salary <= 1500:
                    tax = taxable_salary*3/100
                elif taxable_salary <= 4500:
                    tax = taxable_salary*10/100-105
                elif taxable_salary <= 9000:
                    tax = taxable_salary*20/100-555
                elif taxable_salary <= 35000:
                    tax = taxable_salary*25/100-1005
                elif taxable_salary <= 55000:
                    tax = taxable_salary*30/100-2755
                elif taxable_salary <= 80000:
                    tax = taxable_salary*35/100-5505
                else:
                    tax = taxable_salary*45/100-13505
                salary_after_tax = salary - insure5_1 - tax
                #result_unit = (worker_id,format(salary,'.2f'),"%.2f"%(insure5_1),"%.2f"%(tax),"%.2f"%(salary_after_tax))
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                result_unit = (worker_id,salary,"%.2f"%(insure5_1),"%.2f"%(tax),"%.2f"%(salary_after_tax),now)
                #result.append(result_unit)
                self.result_queue.put(result_unit)
                #print(result_unit)
        return

    def export(self):
        outputfile = self.args.get_arg('-o')
        time.sleep(0.2)
        with open(outputfile,'w+') as f:
            if not self.result_queue.empty():
                for i in range(self.result_queue.qsize()):
                    line = self.result_queue.get()
                    #print(line)
                    writer = csv.writer(f)
                    writer.writerow(line)

if __name__ == '__main__':
    queue1 = Queue()
    queue2 = Queue()
    args = Args()
    config = Config(args)
    userdata = UserData(args,queue1)
    incomeTaxCalculator = IncomeTaxCalculator(config,args,queue1,queue2)

    Process(target=userdata.send_userdata).start()
    Process(target=incomeTaxCalculator.calc_for_all_userdata).start()
    Process(target=incomeTaxCalculator.export).start()
