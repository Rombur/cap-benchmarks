#! /usr/bin/env python
#----------------------------------------------------------------------------#
# Python code
# Author: Bruno Turcksin
# Date: 2016-02-11 16:01:02.714526
#----------------------------------------------------------------------------#

import os
import subprocess
import smtplib
from email.mime.text import MIMEText

#benchmarks_file = open('/scratch/source/cap-benchmarks/benchmarks_test.txt','a')
#print(benchmarks_file)
#benchmarks_file.write('test\n')
#benchmarks_file.close()
#benchmarks_file = open('/scratch/source/cap-benchmarks/benchmarks_test.txt','r')
#print(benchmarks_file.read())
#print(benchmarks_file)

################

# Recompile the Cap and the benchmark using -fsanitize=undefined
os.chdir("/home/bt2/Documents/Cap/build_release")
subprocess.call(["./do_configure", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined"])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir("/home/bt2/Documents/cap-benchmarks")
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make"])
sanitizer_file = open('undefined_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(output)
sanitizer_file.close()
subprocess.call(["make","clean"])

# Recompile the Cap and the benchmark using -fsanitize=address
os.chdir("/home/bt2/Documents/Cap/build_release")
subprocess.call(["./do_configure", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined"])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir("/home/bt2/Documents/cap-benchmarks")
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=address", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make"])
sanitizer_file = open('address_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(output)
sanitizer_file.close()
subprocess.call(["make","clean"])

# Recompile the Cap and the benchmark using -fsanitize=leak
os.chdir("/home/bt2/Documents/Cap/build_release")
subprocess.call(["./do_configure", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined"])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir("/home/bt2/Documents/cap-benchmarks")
subprocess.call(["make", "clean"])
subprocess.call(["make"])
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=leak", "."])
sanitizer_file = open('leak_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(output)
sanitizer_file.close()
subprocess.call(["make","clean"])

# Check that the output is the same in everyfile 
diff_1 = subprocess.Popen(["diff", "undefined_sanititzer.txt",
    "address_sanitizer.txt"], stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE).communicate()[0]
diff_2 = subprocess.Popen(["diff", "undefined_sanititzer.txt",
    "leak_sanitizer.txt"], stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE).communicate()[0]

# Send email
email_file = open('email.txt', 'w')
email_file.write(diff_1)
email_file.write(diff_2)
email_file.close()
email_file = open('email.txt', 'r')
msg = MIMEText(email_file.read())
email_file.close()

msg['Subject'] = 'Cap: sanitizers and benchmarks'
msg['From'] = 'turcksinbr@ornl.gov'
msg['To'] = 'turcksinbr@ornl.gov'

s = smtplib.SMTP('localhost')
s.sendmail('turcksinbr@ornl.gov', 'turcksinbr@ornl.gov', msg.as_string())
s.quit()
