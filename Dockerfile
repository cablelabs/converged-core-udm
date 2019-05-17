FROM python:3

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD udm_api/ /

ENTRYPOINT [ "python", "app.py" ]