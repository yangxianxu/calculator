#-*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys
import os
import csv

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
    def __init__(self,args):
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

class IncomeTaxCalculator(object):
    def calc_for_all_userdata(self, config, userdata):
        result = []
        
        jsl = config.get_config('JiShuL')
        jsh = config.get_config('JiShuH')
        yla = config.get_config('YangLao')
        yli = config.get_config('YiLiao')
        sye = config.get_config('ShiYe')
        gs = config.get_config('GongShang')
        syu = config.get_config('ShengYu')
        gjj = config.get_config('GongJiJin')
        print(userdata)
        for user in userdata:
            worker_id = user[0]
            salary = user[1]
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
            result.append(result_unit)
        print(result)
        return result

    def export(self, config, userdata, args):
        result = self.calc_for_all_userdata(config, userdata)
        outputfile = args.get_arg('-o')
        with open(outputfile,'w') as f:
            writer = csv.writer(f)
            writer.writerows(result)

if __name__ == '__main__':
    args = Args()
    config = Config(args)
    userdata = UserData(args).userdata
    incomeTaxCalculator = IncomeTaxCalculator()
    incomeTaxCalculator.export(config, userdata,args)
