
FROM python:3.8-slim-buster

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN apk update && apk upgrade
RUN apk add chromium chromium-chromedriver

COPY . .

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0"]