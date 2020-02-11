FROM python:3.7-alpine
ADD . /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD [ "python", "./main.py" ]