from datetime import timedelta, datetime
check_for_new_users_interval = timedelta(minutes=1)

start = datetime.now()
print ('start: ', start)

while True:
        now = datetime.now()
        if now == start + check_for_new_users_interval:
            print ('1 minute passed', now)
            start = start + check_for_new_users_interval

