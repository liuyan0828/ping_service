FROM python:3.8-slim-bookworm
# line below is using SOHU.COM@TencentCloud images repository
# FROM cloud-sample.tencentcloudcr.com/ns-qa-prod/qa_basics:1.3.0
COPY . /pingback_service
RUN apt-get update
WORKDIR /pingback_service/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 8813
CMD python ./__main__.py