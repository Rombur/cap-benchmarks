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
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import time
import matplotlib.pylab as plt
import numpy as np

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

# Run benchmark
os.chdir("/home/bt2/Documents/Cap/build_release")
subprocess.call(["./do_configure", "-DCMAKE_CXX_FLAGS=-O3"])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir("/home/bt2/Documents/cap-benchmarks")
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-O3", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make"])
start_time = time.time()
subprocess.call(["./test_exact_transient_solution-2"])
end_time = time.time()
subprocess.call(["make","clean"])
benchmark_file = open('benchmark_1.txt', 'a')
delta_t = end_time-start_time
benchmark_file.write(str(delta_t)+'\n')
benchmark_file.close()
benchmark_file = open('benchmark_1.txt', 'r')
data = benchmark_file.read()
data_list = data.split()
data_array = np.array(data_list)
plt.plot(data_array)
plt.ylabel('Time in seconds')
plt.xlabel('Run')
plt.title('Benchmark')
plt.savefig('benchmark.png')


# Send email
msg = MIMEMultipart()
email_file = open('email.txt', 'w')
email_file.write('The sanitizers found the following error:')
email_file.write(diff_1)
email_file.write(diff_2)
email_file.close()
email_file = open('email.txt', 'r')
msg.attach(MIMEText(email_file.read()))
email_file.close()

fp = open('benchmark.png', 'rb')
img = MIMEImage(fp.read());
fp.close()
msg.attach(img)

msg['Subject'] = 'Cap: sanitizers and benchmarks'
msg['From'] = 'turcksinbr@ornl.gov'
msg['To'] = 'turcksinbr@ornl.gov'

s = smtplib.SMTP('localhost')
s.sendmail('turcksinbr@ornl.gov', 'turcksinbr@ornl.gov', msg.as_string())
s.quit()
