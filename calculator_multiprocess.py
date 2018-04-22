#-*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys
import os
import csv
from multiprocessing import Process, Queue
import time
class Args(object):
    def __init__(self):
        self.args = sys.argv[1:]

    def get_arg(self,index_arg):
        try:
            index = self.args.index(index_arg)
            file_path = self.args[index+1]
        except ValueError:
            print('Argument Error')
        return file_path

class Config(object):
    def __init__(self, args):
        self.config = self._read_config(args)

    def _read_config(self,args):
        config = {}
        configfile = args.get_arg('-c')
        with open(configfile) as file:
            for line in file:
                try:
                    i = line.split('=')
                    config[str(i[0].strip())] = float(i[1].strip().replace("\n",""))
                except ValueError:
                    print('Config Data Error')
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
        jsl = self.config.get_config('JiShuL')
        jsh = self.config.get_config('JiShuH')
        yla = self.config.get_config('YangLao')
        yli = self.config.get_config('YiLiao')
        sye = self.config.get_config('ShiYe')
        gs = self.config.get_config('GongShang')
        syu = self.config.get_config('ShengYu')
        gjj = self.config.get_config('GongJiJin')
        print(gjj)
        if not self.task_queue.empty():
            for i in range(self.task_queue.qsize()):
                user_m = self.task_queue.get()
                print(user_m)
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
                result_unit = (worker_id,salary,"%.2f"%(insure5_1),"%.2f"%(tax),"%.2f"%(salary_after_tax))
                #result.append(result_unit)
                self.result_queue.put(result_unit)
                print(result_unit)
        return

    def export(self):
        outputfile = self.args.get_arg('-o')
        time.sleep(0.2)
        with open(outputfile,'w+') as f:
            if not self.result_queue.empty():
                for i in range(self.result_queue.qsize()):
                    line = self.result_queue.get()
                    print(line)
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
