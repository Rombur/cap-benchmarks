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

cap_build="/scratch/build/Cap"
cap_benchmarks="/scratch"
os.environ['LD_LIBRARY_PATH']="/opt/boost/1.60.0/lib"

# Recompile the Cap and the benchmark using -fsanitize=undefined
os.chdir(cap_build)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined", "."])
subprocess.call(["make", "clean"])
os.chdir(cap_benchmarks)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=undefined", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make"])
subprocess.call(["./test_exact_transient_solution-2"])
sanitizer_file = open('undefined_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./charge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./cyclic_voltammetry"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./discharge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
sanitizer_file.close()
subprocess.call(["make","clean"])

# Recompile the Cap and the benchmark using -fsanitize=address
os.chdir(cap_build)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=address", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir(cap_benchmarks)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=address", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make"])
subprocess.call(["./test_exact_transient_solution-2"])
sanitizer_file = open('address_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./charge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./cyclic_voltammetry"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./discharge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
sanitizer_file.close()
subprocess.call(["make","clean"])

# Recompile the Cap and the benchmark using -fsanitize=leak
os.chdir(cap_build)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=leak", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir(cap_benchmarks)
subprocess.call(["make", "clean"])
subprocess.call(["make"])
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-fsanitize=leak", "."])
subprocess.call(["./test_exact_transient_solution-2"])
sanitizer_file = open('leak_sanitizer.txt', 'w')
output = subprocess.Popen(["./test_exact_transient_solution-2"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./charge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./cyclic_voltammetry"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
output = subprocess.Popen(["./discharge_curve"], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
sanitizer_file.write(str(output))
sanitizer_file.close()
subprocess.call(["make","clean"])

# Check that the output is the same in everyfile 
diff_1 = subprocess.Popen(["diff", "undefined_sanitizer.txt",
    "address_sanitizer.txt"], stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE).communicate()[0]
diff_2 = subprocess.Popen(["diff", "undefined_sanitizer.txt",
    "leak_sanitizer.txt"], stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE).communicate()[0]

# Run benchmark
os.chdir(cap_build)
subprocess.call(["cmake", "-DCMAKE_CXX_FLAGS=-O3", "."])
subprocess.call(["make", "clean"])
subprocess.call(["make", "-j4", "install"])
os.chdir(cap_benchmarks)
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
email_file.write(str(diff_1)[2:-1])
email_file.write(str(diff_2)[2:-1])
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
