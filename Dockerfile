############################################################
# Dockerfile to build New Employee Onboarding App
############################################################
#sometimes need to build without cache

#docker build -t new-employee-onboarding .
#docker run -i -t new-employee-onboarding
###########################################################################

FROM python:3.12.9

# File Author / Maintainer
MAINTAINER "Victor Vazquez <vvazquez@cisco.com>"

# Copy the application folder inside the container
ADD . .

# Set the default directory where CMD will execute
WORKDIR /

# Get pip to download and install requirements:
RUN pip install -r requirements.txt


# Set the default command to execute
# when creating a new container
CMD ["python","-u","app.py"]