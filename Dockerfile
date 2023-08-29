FROM mindsgo-sz-docker.pkg.coding.net/neuroimage_analysis/base/msg_baseimage_cuda11:deepFS
MAINTAINER Chenfei <chenfei.ye@foxmail.com>

RUN apt update
	
	
RUN	pip install -i https://mirrors.aliyun.com/pypi/simple/ loguru \
	argparse 
	

COPY ./ /pipeline
RUN chmod 777 -R /pipeline/
WORKDIR /workspace
ENTRYPOINT ["python", "/pipeline/run_docker.py"]
