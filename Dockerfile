# Python $B$N%Y!<%9%$%a!<%8$r;HMQ(B
FROM python:3.11

# $B:n6H%G%#%l%/%H%j$N@_Dj(B
WORKDIR /app

# $BI,MW$J(BPython$B%i%$%V%i%j$r%$%s%9%H!<%k$9$k$?$a$N(B requirements.txt $B%U%!%$%k$r%3%T!<(B
COPY requirements.txt ./

# requirements.txt $B$K%j%9%H$5$l$F$$$k0MB84X78$r%$%s%9%H!<%k(B
RUN pip install --no-cache-dir -r requirements.txt

# recv_event_hub.py $B$r%3%s%F%JFb$N:n6H%G%#%l%/%H%j$K%3%T!<(B
COPY recv_service_bus.py ./

# $B%3%s%F%J5/F0;~$K(B Python $B%9%/%j%W%H$r<B9T(B
CMD [ "python", "./recv_service_bus.py" ]
